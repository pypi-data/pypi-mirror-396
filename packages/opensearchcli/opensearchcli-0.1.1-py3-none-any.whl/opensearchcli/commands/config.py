import os
import tomlkit
from typing import Annotated, Sequence

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    rich_markup_mode="rich",
    no_args_is_help=True,
    help="Introspect available CLI commands",
)
console = Console()


class ConfigProfile:
    def __init__(self, profile_name: str, data: dict) -> None:
        self.profile_name = profile_name
        self._data = data

    @property
    def domain(self) -> str:
        return self._data.get("domain", "")

    @property
    def username(self) -> str:
        return self._data.get("username", "")

    @property
    def password(self) -> str:
        return self._data.get("password", "")

    def __str__(self) -> str:
        return (
            f"Profile Name: {self.profile_name}\n"
            f"\tDomain: {self.domain}\n"
            f"\tUsername: {self.username}\n"
            f"\tPassword: {'*' * len(self.password) if self.password else ''}"
        )

    def to_toml(self):
        return (
            tomlkit.table()
            .add("domain", self.domain)
            .add("username", self.username)
            .add("password", self.password)
        )


class Config:
    def __init__(self, file_loc: str, profiles: list[ConfigProfile]) -> None:
        self.file = file_loc
        self.profiles = profiles

    def find_profile_by_name(self, profile_name: str) -> ConfigProfile:
        for profile in self.profiles:
            if profile.profile_name == profile_name:
                return profile
        return ConfigProfile(profile_name="", data={})


def read_config(config_file: str) -> Config:
    if not os.path.isfile(path=config_file):
        return Config(file_loc="", profiles=[ConfigProfile(profile_name="", data={})])

    try:
        with open(file=config_file, mode="rb") as _file:
            data = tomlkit.load(_file)
    except ValueError as error:
        data = {}
        print(f"invalid toml: {error}")
    return Config(
        file_loc=config_file,
        profiles=[
            ConfigProfile(profile_name=profile_name, data=data[profile_name])
            for profile_name in data.keys()
        ],
    )


def _get_profiles_table(profiles: Sequence[ConfigProfile]) -> Table:
    table = Table(show_header=True, header_style="cyan")
    table.add_column(header="Profile Name")
    table.add_column(header="Domain")
    table.add_column(header="Username")
    table.add_column(header="Password")
    for profile in profiles:
        table.add_row(
            f"{profile.profile_name}",
            f"{profile.domain}",
            f"{profile.username}",
            f"{profile.password}",
        )
    return table


@app.command(name="list")
def list_profiles(ctx: typer.Context) -> None:
    """List all configuration profiles.

    Display a table showing all configured profiles with their details.
    """
    console.print(_get_profiles_table(profiles=ctx.obj.config.profiles))


@app.command(
    name="show",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def show_profile(ctx: typer.Context, profile_name: str = "default") -> None:
    """Show details for a specific configuration profile.

    Display the profile information for the given profile name.

    Args:
        profile_name: Name of the profile to display (default: "default")
    """
    _profile = ctx.obj.config.find_profile_by_name(profile_name)
    if not _profile:
        typer.echo(message=f"No profile found for: {profile_name}")
        return None
    console.print(_get_profiles_table(profiles=[_profile]))


def _create_config_data(
    domain: str, username: str, password: str
) -> tomlkit.TOMLDocument:
    return (
        tomlkit.table()
        .add("domain", domain)
        .add("username", username)
        .add("password", password)
    )


@app.command(name="add-profile")
def add_profile(
    ctx: typer.Context,
    password: Annotated[str, typer.Option(prompt=True, hide_input=True)],
    profile_name: Annotated[str, typer.Option()],
    domain: Annotated[str, typer.Option()],
    username: Annotated[str, typer.Option()],
    overwrite: Annotated[bool, typer.Option()] = False,
) -> None:
    """Create a new configuration file with default profile.

    This command will prompt for domain, username, and password, then create
    a configuration file at the specified location.
    """
    config_file = ctx.obj.config_file_path

    config_profiles = tomlkit.document()
    if os.path.isfile(path=config_file):
        with open(file=config_file, mode="rb") as _file:
            config_profiles = tomlkit.load(_file)

    if profile_name in config_profiles and not overwrite:
        console.print(
            f"[red]Profile '{profile_name}' already exists in {config_file}. Use --overwrite to replace it.[/red]"
        )
        raise typer.Exit(code=1)

    config_profiles[profile_name] = _create_config_data(
        domain=domain, username=username, password=password
    )

    os.makedirs(name=os.path.dirname(config_file), exist_ok=True)
    with open(file=config_file, mode="w") as _file:
        tomlkit.dump(config_profiles, _file)

    console.print(
        f"[green]✓ Configuration created successfully at {config_file}[/green]"
    )
