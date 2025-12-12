from typing import List

import typer
from rich.console import Console

from opensearchcli.commands.helpers import body_dict_from_flags, parse_params

app = typer.Typer(
    rich_markup_mode="rich",
    no_args_is_help=True,
    help="Manage OpenSearch index settings",
)
console = Console()


@app.command()
def get(
    ctx: typer.Context,
    index: str = typer.Argument(help="The name of the index to retrieve settings for"),
    params: List[str] = typer.Option(
        default=[], help="Settings parameters to retrieve"
    ),
):
    """Retrieve settings for a specific index."""

    _params = parse_params(params)

    settings = ctx.obj.opensearch.indices.get_settings(index=index, params=_params)
    console.print(settings)


@app.command()
def set(
    ctx: typer.Context,
    index: str = typer.Argument(help="The name of the index to update settings for"),
    settings: List[str] = typer.Argument(
        help="Settings to update in the format key=value"
    ),
):
    """Update settings for a specific index."""
    payload = body_dict_from_flags(settings)
    response = ctx.obj.opensearch.indices.put_settings(index=index, body=payload)
    console.print(response)
