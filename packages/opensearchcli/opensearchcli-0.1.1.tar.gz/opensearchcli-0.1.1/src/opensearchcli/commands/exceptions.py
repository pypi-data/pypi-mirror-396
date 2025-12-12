from functools import wraps

import typer
from rich.console import Console

console = Console()


def catch_exception(which_exception, exit_code=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except which_exception as e:
                console.print(f"[red]Error:[/red] {str(e)}")
                raise typer.Exit(code=exit_code)

        return wrapper

    return decorator
