from typing import List

import typer
from rich.console import Console

from opensearchcli.commands.helpers import body_dict_from_flags, parse_params

app = typer.Typer(
    rich_markup_mode="rich",
    no_args_is_help=True,
    help="Make raw API calls to OpenSearch cluster",
)
console = Console()


@app.command()
def do(
    ctx: typer.Context,
    method: str = typer.Argument("GET", help="HTTP method to use"),
    endpoint: str = typer.Argument(help="API endpoint to call"),
    body: List[str] = typer.Option({}, help="Request body for POST/PUT requests"),
    params: List[str] = typer.Option({}, help="Query parameters for the request"),
):
    """Make a raw API call to the OpenSearch cluster."""
    opensearch = ctx.obj.opensearch

    payload = body_dict_from_flags(body)
    query_params = parse_params(params)

    response = opensearch.transport.perform_request(
        method,
        endpoint,
        body=payload if body else None,
        params=query_params if params else None,
    )
    console.print(response)
