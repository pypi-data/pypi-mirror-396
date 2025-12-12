from typing import Annotated, List

import typer
from opensearchpy import RequestError
from rich.console import Console

app = typer.Typer(
    rich_markup_mode="rich",
    no_args_is_help=True,
    help="Manage OpenSearch cluster settings",
)
console = Console()


@app.command()
def get(
    ctx: typer.Context,
    params: Annotated[
        list[str], typer.Option(help="Cluster settings to retrieve")
    ] = [],
):
    """Retrieve cluster settings."""
    _params = {}
    for p in params:
        if "=" in p:
            key, value = p.split("=", 1)
            _params[key] = value
        else:
            _params[p] = "true"
    _settings = ctx.obj.opensearch.cluster.get_settings(params=_params)
    console.print(_settings)


@app.command()
def set(ctx: typer.Context, settings: List[str]):
    """Update cluster settings."""

    body = {
        "persistent": {},
    }
    for s in settings:
        name, value = s.split("=", 1)
        body["persistent"][name] = value

    try:
        ctx.obj.opensearch.cluster.put_settings(body=body)
        console.print(
            f"[green]Successfully updated settings:[/green] {body['persistent']}"
        )
    except RequestError as e:
        console.print(f"[red]Error updating settings:[/red] {e.info}")
