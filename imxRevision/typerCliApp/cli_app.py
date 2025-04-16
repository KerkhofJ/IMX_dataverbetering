from pathlib import Path
from typing import Annotated

import typer
from rich import print
from rich.panel import Panel
from rich.console import Console

from utils.input_validation import validate_process_input, InputValidationError

app = typer.Typer()

state = {
    "verbose": False,
    "debug": False,
}

console = Console()


@app.command()
def create_template():
    pass


@app.command()
def process(
    imx_input: Annotated[Path, typer.Option(help="The input imx file as a xml file.")],
    excel_input: Annotated[Path, typer.Option(help="The input excel whit items to process.")],
    out_path: Annotated[Path, typer.Option(help="The output folder for processed imx and excel report.")],
):
    try:
        validate_process_input(imx_input, excel_input, out_path)
    except InputValidationError as e:
        console.print(Panel("\n".join(e.errors), title="[bold red]Invalid Input[/bold red]", expand=True))
        raise typer.Exit(code=1)



@app.callback()
def main(verbose: bool = False, debug: bool = False):
    """
    Awesome CLI app.
    """
    if verbose:
        print("[blue]Verbose mode enabled[/blue]")
        state["verbose"] = True

    if debug:
        print("[blue]Debug mode enabled[/blue]")
        state["debug"] = True



if __name__ == "__main__":
    app()