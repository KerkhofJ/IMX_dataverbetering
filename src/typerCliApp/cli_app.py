from pathlib import Path
from typing import Annotated

import typer
from rich import print
from rich.panel import Panel
from rich.console import Console


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
    out_path: Annotated[Path, typer.Option(help="Last name of person to greet.")],
):
    input_errors = []

    if not imx_input.exists():
        input_errors.append(f"[red]❌ imx_input does not exist: [bold]{imx_input}[/bold][/red]")
    elif not imx_input.suffix == '.xml':
        input_errors.append(f"[red]❌ imx_input is not a xml file: [bold]{imx_input}[/bold][/red]")

    imx_output = imx_input.with_name(f"{imx_input.stem}-processed{imx_input.suffix}")

    if not excel_input.exists():
        input_errors.append(f"[red]❌ excel_input does not exist: [bold]{excel_input}[/bold][/red]")
    elif not excel_input.suffix == '.xlsx' or not excel_input.suffix == '.xlsm':
        input_errors.append(f"[red]❌ excel_input is not a excel file: [bold]{imx_input}[/bold][/red]")

    excel_output = imx_input.with_name(f"{excel_input.stem}-processed{excel_input.suffix}")

    if input_errors:
        console.print(Panel("\n".join(input_errors), title="[bold red]Invalid Input[/bold red]", expand=False))
        raise typer.Exit(code=1)


    print("[green]✔ Inputs look good. Proceeding...[/green]")


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