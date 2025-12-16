import typer
from dbt_swap.cli import smart_build, get_manifest

app = typer.Typer(help="dbt-swap CLI — utilities around dbt state and builds")


# Shared context init (runs before each command)
@app.callback(invoke_without_command=True)
def main():
    """Initialize shared CLI context."""


# Register subcommands
app.command("smart-build")(smart_build.smart_build)
app.command("get-manifest")(get_manifest.get_manifest)

if __name__ == "__main__":
    app()
