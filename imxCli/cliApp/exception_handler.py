import typer
from rich.panel import Panel
from rich.console import Console

from imxCli.utils.exceptions import ErrorList

console = Console()


def handle_input_validation(func):
    """Decorator to handle InputValidationError exceptions in a reusable way."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ErrorList as e:
            console.print(
                Panel(
                    "\n".join(e.errors),
                    title="[bold red]Invalid Input[/bold red]",
                    expand=True,
                )
            )
            raise typer.Exit(code=1)

    return wrapper
