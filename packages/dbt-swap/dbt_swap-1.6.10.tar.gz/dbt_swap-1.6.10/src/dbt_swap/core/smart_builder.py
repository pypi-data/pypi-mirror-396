from pathlib import Path
from sqlglot import parse_one, exp
import json
import os
from dbt_swap.utils.logging import get_logger
from dbt_swap.utils.run_dbt import run_dbt
from functools import cached_property

logger = get_logger(__name__)


class DbtSmartBuilder:
    def __init__(self, dialect: str = "redshift", verbose: bool = False):
        # Allow overriding paths via environment for correctness with dbt --state and target-path
        # DBT_STATE: directory containing a manifest.json representing the comparison state
        # DBT_TARGET_STATE: directory containing the current target manifest.json (after compile)
        self.target_dir = os.environ.get("DBT_TARGET_STATE", "./target")
        self.state_dir = os.environ.get("DBT_STATE", "./state")
        self.target_manifest_path = str(Path(self.target_dir) / "manifest.json")
        self.state_manifest_path = str(Path(self.state_dir) / "manifest.json")
        self.dialect = dialect
        self.verbose = verbose
        self.ignored_columns = [
            col.strip() for col in os.environ.get("DBT_SMART_IGNORED_COLUMNS", "").split(",") if col.strip()
        ]

    def list_changed_node_ids(self, downstream: bool = False) -> list[str]:
        """Get list of changed node unique ids using dbt ls command."""
        logger.info("Getting changed nodes...")
        if downstream:
            selector = "state:modified+"
        else:
            selector = "state:modified"
        _, output = run_dbt(["dbt", "ls", "--select", selector, "--output", "json", "--quiet"])

        changed_files = [json.loads(line) for line in output]
        changed_node_ids = [node["unique_id"] for node in changed_files]

        return changed_node_ids

    @cached_property
    def modified_node_ids(self) -> list[str]:
        """Get list of changed models using dbt ls command."""
        return self.list_changed_node_ids(downstream=False)

    @cached_property
    def modified_and_downstream_node_ids(self) -> list[str]:
        """Get list of changed models and their downstream dependencies using dbt ls command."""
        return self.list_changed_node_ids(downstream=True)

    def compile_changed_nodes(self) -> None:
        """Compile changed nodes and their dependencies using dbt compile command."""
        logger.info("Compiling changed models and dependencies...")
        run_dbt(
            [
                "dbt",
                "compile",
                "--select",
                "state:modified+",
                "--quiet",
                "--state",
                self.state_dir,
            ]
        )

    def load_manifest(self, manifest_path) -> dict:
        """Load manifest from the given path."""
        path = Path(manifest_path)
        if not path.exists():
            logger.error(f"Manifest not found at {manifest_path}. Run 'dbt compile' first.")
            raise FileNotFoundError(f"Manifest not found at {manifest_path}. Run 'dbt compile' first.")

        with open(path) as f:
            manifest = json.load(f)

        return manifest

    @cached_property
    def manifest(self) -> dict:
        return self.load_manifest(self.target_manifest_path)

    @cached_property
    def compare_manifest(self) -> dict:
        return self.load_manifest(self.state_manifest_path)

    @cached_property
    def nodes(self) -> dict:
        """Get nodes from the target manifest."""
        return self.manifest.get("nodes", {})

    @cached_property
    def compare_nodes(self) -> dict:
        """Get nodes from the state manifest."""
        return self.compare_manifest.get("nodes", {})

    @cached_property
    def child_map(self) -> dict:
        """Return the child map from target manifest."""
        return self.manifest.get("child_map", {})

    def find_changed_columns(self, node: dict) -> list[str]:
        """Find columns that have changed in a node."""
        if node["resource_type"] != "model":
            return []

        sql = node.get("compiled_code", "select 1")
        compare_sql = self.compare_nodes.get(node["unique_id"], {}).get("compiled_code", "select 1")

        try:
            parsed = [
                projection
                for select in parse_one(sql, dialect=self.dialect).find_all(exp.Select)
                for projection in select.expressions
            ]
            compare_parsed = [
                projection
                for select in parse_one(compare_sql, dialect=self.dialect).find_all(exp.Select)
                for projection in select.expressions
            ]

            diffs = set(parsed) ^ set(compare_parsed)
            columns = [change.alias_or_name for change in diffs]
            if columns == ["*"]:
                return []  # Returning an empty list signals that all columns have changed, which triggers different downstream handling logic.
            if "*" in columns:
                columns.remove("*")
            # Filter out ignored columns
            columns = [col for col in columns if col not in self.ignored_columns]
            return columns
        except Exception as e:
            logger.warning(f"Could not parse SQL for node {node['name']}: {e}")
            return []

    def find_column_refs(
        self,
        node: dict,
        changed_column: str,
        refs: list[exp.Expression] | None = None,
        visited: set[str] | None = None,
        from_node: dict = {},
    ) -> list[str]:
        """Find references to changed columns in a node."""
        if refs is None:
            sql = node.get("compiled_code", "select 1")
            refs = [
                projection
                for select in parse_one(sql, dialect=self.dialect).find_all(exp.Select)
                for projection in select.expressions
            ]
            # If the model selects all columns, consider all changed columns as referenced
            if set(refs) == {exp.Star()}:
                return [changed_column]

        if visited is None:
            visited = set()

        if changed_column in visited:
            return []

        visited.add(changed_column)
        column_refs = []

        for ref in refs:
            # If the reference matches the changed column, add it to the list
            if ref.alias_or_name == changed_column:
                column_refs.append(ref.alias_or_name)
            # If the reference is a star and matches the from_node, add the changed column
            elif (
                isinstance(ref, exp.Column)
                and ref.this == exp.Star()
                and hasattr(ref, "table")
                and ref.table is not None
            ):
                if ref.table in from_node.get("name", ""):
                    column_refs.append(changed_column)
            # If the reference is a column, check if it matches the changed column
            elif isinstance(ref, exp.Alias):
                for col in ref.this.find_all(exp.Column):
                    if col.alias_or_name == changed_column:
                        column_refs.append(ref.alias_or_name)

        column_refs = [col for col in column_refs if col not in self.ignored_columns]

        # If there are no new column references, return an empty set to avoid infinite recursion
        if column_refs:
            for column_ref in set(column_refs):
                column_refs.extend(self.find_column_refs(node, column_ref, refs, visited, from_node=from_node))

        # Recursively find column references
        return column_refs

    def search_in_graph(
        self,
        changed_node_id: str,
        changed_columns: list[str],
        all: bool = False,
    ) -> list[str]:
        """Recursively search for models affected by column changes."""

        affected = [changed_node_id]

        for child_id in self.child_map.get(changed_node_id, []):
            child_node = self.nodes.get(child_id, {})
            node = self.nodes.get(changed_node_id, {})
            if not child_node:
                continue
            # If no specific columns changed, all downstream nodes are affected
            if all:
                if self.verbose:
                    logger.info(
                        f"{child_node['resource_type']} {child_node['name']} is affected by changes in {changed_node_id} (node changed entirely)"
                    )
                affected.extend(self.search_in_graph(child_id, changed_columns, all=all))
            else:
                # If the changed_model or child is not a model (e.g., a snapshot or seed), consider it affected
                if node["resource_type"] != "model" or child_node["resource_type"] != "model":
                    if self.verbose:
                        logger.info(
                            f"{child_node['resource_type']} {child_node['name']} is affected by changes in {changed_node_id}"
                        )
                    affected.extend(self.search_in_graph(child_id, changed_columns))
                    continue

                # If the model selects all columns, consider all changed columns as referenced
                column_refs = list(
                    {
                        column_ref
                        for changed_column in changed_columns
                        for column_ref in self.find_column_refs(child_node, changed_column, from_node=node)
                    }
                )

                # If there are column references, consider the node affected
                if column_refs:
                    if self.verbose:
                        logger.info(
                            f"{child_node['resource_type']} {child_node['name']} is affected by changes in {changed_node_id}, columns: {column_refs}"
                        )
                    affected.extend(self.search_in_graph(child_id, column_refs))

        return list(set(affected))

    def find_modified_nodes(self) -> list[str]:
        """Find all nodes affected by changes."""
        logger.info("🧠 Starting smart model selection...")

        if not self.modified_node_ids:
            logger.info("No modified nodes found.")
            return []

        self.compile_changed_nodes()

        affected_nodes = set()
        for changed_node_id in self.modified_node_ids:
            changed_node = self.nodes.get(changed_node_id)
            if changed_node is None:
                continue
            changed_columns = self.find_changed_columns(changed_node)
            column_refs = list(
                {
                    column_ref
                    for changed_column in changed_columns
                    for column_ref in self.find_column_refs(changed_node, changed_column)
                }
                | set(changed_columns)
            )

            # If no specific columns changed, treat it as a full change
            all = len(column_refs) == 0
            if all:
                if self.verbose:
                    logger.info(f"Changed node: {changed_node['name']}")
            else:
                if self.verbose:
                    logger.info(f"Changed model: {changed_node['name']} with changed columns: {column_refs}")

            affected_nodes.update(self.search_in_graph(changed_node_id, column_refs, all=all))

        return list([self.nodes[affected_node]["name"] for affected_node in affected_nodes])
