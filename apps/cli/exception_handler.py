import typer
from rich.console import Console
from rich.panel import Panel

from imxTools.utils.exceptions import ErrorList

console = Console()


# TODO: Create methode instead of decorator (more clean less issues)


def handle_exceptions(func):
    """
    Decorator to handle InputValidationError, ValueError exceptions in a reusable way.

    Decorator should be placed before the cli command decorator!
    """

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

        except ValueError as e:
            console.print(
                Panel(
                    f"{e}",
                    title="[bold red]Invalid Input[/bold red]",
                    expand=True,
                )
            )
            raise typer.Exit(code=1)

    return wrapper
