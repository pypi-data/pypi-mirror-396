import os
from typing import Annotated

import typer
from pathlib import Path
from opensearchpy import OpenSearch
from rich.console import Console
from opensearchcli.commands import cluster, config, snapshot, commands, raw, index
import urllib3

urllib3.disable_warnings()

console = Console()
app = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)
app.add_typer(typer_instance=commands.app, name="commands")
app.add_typer(
    typer_instance=cluster.app, name="cluster", help="OpenSearch cluster api commands"
)
app.add_typer(
    typer_instance=index.app, name="index", help="OpenSearch index api commands"
)
app.add_typer(
    typer_instance=snapshot.app,
    name="snapshot",
    help="OpenSearch snapshot api commands",
)
app.add_typer(typer_instance=raw.app, name="raw", help="Make raw OpenSearch API calls")


class OpenSearchCli:
    def __init__(
        self,
        config: config.Config,
        profile: config.ConfigProfile,
        config_file_path: str,
    ) -> None:
        self._opensearch: OpenSearch | None = None
        self.config = config
        self.profile = profile
        self.config_file_path = config_file_path

    @property
    def opensearch(self) -> OpenSearch:
        if self._opensearch is None:
            self._opensearch = OpenSearch(
                hosts=[
                    {
                        "host": self.profile.domain,
                        "port": 9200,
                    }
                ],
                http_auth=(self.profile.username, self.profile.password),
                use_ssl=True,
                verify_certs=False,
                ssl_show_warn=False,
            )
        return self._opensearch


@app.callback()
def common(
    ctx: typer.Context,
    config_file: Annotated[str, typer.Option()] = os.path.expanduser(
        path=f"{Path.home()}/.config/opensearch-cli/config.toml"
    ),
    profile: Annotated[
        str,
        typer.Option(help="OpenSearch profile name", envvar="OPENSEARCH_PROFILE"),
    ] = "default",
    raw: bool = Annotated[
        bool, typer.Option(help="Display raw JSON output", default=False)
    ],
) -> None:
    """OpenSearch CLI - Manage your OpenSearch clusters."""

    _config = config.read_config(config_file=config_file)
    _profile = _config.find_profile_by_name(profile_name=profile)

    ctx.obj = OpenSearchCli(
        config=_config,
        profile=_profile,
        config_file_path=config_file,
    )


if __name__ == "__main__":
    app()
