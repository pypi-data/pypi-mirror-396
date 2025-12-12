
# OpenSearch CLI

OpenSearch CLI is a command-line tool to manage and interact with OpenSearch clusters. It provides commands for cluster management, snapshots, raw API calls, and more, all from your terminal.

## Features

- Manage OpenSearch clusters (health, settings, allocation, etc.)
- Run raw OpenSearch API calls
- Manage snapshots
- Profile-based configuration

## Requirements

- Python 3.14+

## Installation

Clone the repository and install dependencies using [uv](https://github.com/astral-sh/uv):

```sh
git clone <repo-url>
cd OpenSearch
uv sync
```

Or, to run commands directly with uv (no manual activation needed):

```sh
uv run opensearchcli --help
```

## Usage

Run the CLI:

```sh
opensearchcli --help
```

Example: Check cluster health

```sh
opensearchcli cluster health
```

## Configuration

The CLI uses a config file (default: `~/.config/opensearch-cli/config.toml`) to store connection profiles. You can specify a profile with `--profile` or the `OPENSEARCH_PROFILE` environment variable.

Example config file:

```toml
[default]
domain = "localhost"
username = "admin"
password = "admin"
```

## Project Structure

- `src/opensearchcli/cli.py` — Main CLI entry point
- `src/opensearchcli/commands/` — Command modules (cluster, snapshot, etc.)

## Dependencies

- [opensearch-py](https://pypi.org/project/opensearch-py/)
- [typer](https://pypi.org/project/typer/)
- [rich](https://pypi.org/project/rich/)

## License

MIT (add your license here)

