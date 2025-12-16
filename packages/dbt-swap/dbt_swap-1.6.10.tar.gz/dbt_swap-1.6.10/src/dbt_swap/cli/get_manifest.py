import typer
import os
from dbt_swap.utils.logging import get_logger
from boto3 import client

logger = get_logger(__name__)


app = typer.Typer(
    help="Retrieve manifest from s3.",
)


@app.command("get-manifest")
def get_manifest(
    ctx: typer.Context,
    target: str = typer.Option("dev", "--target", "-t", help="DBT target name."),
    state: str = typer.Option("state", "--state", help="DBT state name."),
):
    """
    Retrieve the manifest.json file from the S3 bucket and save it to the local state/ directory.
    """
    s3_client = client("s3")
    os.makedirs("state", exist_ok=True)
    if "dev" in target:
        target_path = "dev_prod"
    else:
        target_path = "prod"
    logger.info(
        f"Downloading manifest from ticketswap-redshift-reporting/dbt/{target_path}/manifest.json to {state}/manifest.json"
    )
    try:
        s3_client.download_file(
            "ticketswap-redshift-reporting", f"dbt/{target_path}/manifest.json", f"{state}/manifest.json"
        )
    except Exception as e:
        logger.error(f"Error downloading manifest: {e}")
        raise typer.Exit(code=1)
