import typer
from rich.console import Console

app = typer.Typer(
    rich_markup_mode="rich", no_args_is_help=True, help="Manage snapshots"
)
console = Console()


@app.command()
def repository(ctx: typer.Context):
    """Get snapshot information."""
    snapshot_info = ctx.obj.opensearch.snapshot.get_repository()
    console.print(snapshot_info)
