import typer
from rich.console import Console

from opensearchcli.commands import index_settings

app = typer.Typer(
    rich_markup_mode="rich",
    no_args_is_help=True,
    help="Manage OpenSearch index operations",
)
app.add_typer(index_settings.app, name="settings", help="Manage index settings")
console = Console()


@app.command()
def list(
    ctx: typer.Context,
    index_pattern: str = typer.Argument(
        ..., help="Index name or pattern to list indices"
    ),
):
    indices = ctx.obj.opensearch.indices.get(index=index_pattern)
    for index_name in indices.keys():
        console.print(index_name)


@app.command()
def get(
    ctx: typer.Context,
    index: str = typer.Argument(
        help="The name of the index to retrieve information for"
    ),
):
    """Retrieve information for a specific index."""
    index_info = ctx.obj.opensearch.indices.get(index=index)
    console.print(index_info)
