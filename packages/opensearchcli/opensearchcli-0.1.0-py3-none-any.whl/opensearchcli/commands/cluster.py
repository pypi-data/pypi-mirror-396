from typing import Annotated

import typer
from opensearchpy import RequestError
from rich.console import Console

from opensearchcli.commands import cluster_settings
from opensearchcli.commands.exceptions import catch_exception

app = typer.Typer(
    rich_markup_mode="rich",
    no_args_is_help=True,
    help="Manage OpenSearch cluster operations",
)
app.add_typer(cluster_settings.app, name="settings", help="Manage cluster settings")
console = Console()


@app.command()
def info(
    ctx: typer.Context,
):
    """Retrieve cluster information."""
    info = ctx.obj.opensearch.info()
    console.print(info)


@app.command()
def health(
    ctx: typer.Context,
):
    """Check the health of the OpenSearch cluster."""
    health = ctx.obj.opensearch.cluster.health()
    console.print(health)


@app.command()
@catch_exception(RequestError, exit_code=1)
def allocation_explain(
    ctx: typer.Context,
    index: Annotated[
        str, typer.Argument(help="The name of the index to explain allocation for")
    ] = None,
):
    """Explain shard allocation for a specific index."""
    if index:
        explanation = ctx.obj.opensearch.cluster.allocation_explain(index=index)
    else:
        explanation = ctx.obj.opensearch.cluster.allocation_explain()

    console.print(explanation)


@app.command()
def pending_tasks(
    ctx: typer.Context,
):
    """List pending tasks in the OpenSearch cluster."""
    tasks = ctx.obj.opensearch.cluster.pending_tasks()
    console.print(tasks)


@app.command()
def stats(ctx: typer.Context):
    """Retrieve cluster statistics."""
    stats = ctx.obj.opensearch.cluster.stats()
    console.print(stats)
