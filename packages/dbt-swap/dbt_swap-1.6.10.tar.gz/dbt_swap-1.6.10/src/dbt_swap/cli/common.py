import os


def set_env(target: str | None = None, state: str | None = None):
    """Set environment variables for all dbt-swap commands."""
    if target:
        os.environ["DBT_TARGET"] = target
    if state:
        os.environ["DBT_STATE"] = state
