from pathlib import Path
from typing import Annotated

import typer
from rich import print
from rich.console import Console

from imxCli.cliApp.exception_handler import handle_input_validation
from imxCli.utils.input_validation import validate_process_input
from imxCli.revision.process_revision import process_imx_revisions

app = typer.Typer()

state = {
    "verbose": False,
    "debug": False,
}

console = Console()



@app.command()
def diff():
    #TODO: create diff cli command
    pass


@app.command()
def geojsons():
    # TODO: create geojson cli command
    pass


@app.command()
def create_manifest():
    # TODO: create manifest cli command
    pass


@app.command()
def validate_manifest():
    # TODO: validate manifest cli command
    pass


@app.command()
def revision_template():
    # TODO: create revision template excel
    pass


@app.command()
@handle_input_validation
def process_revision(
    imx_input: Annotated[Path, typer.Option(help="The input imx file as a xml file.")],
    excel_input: Annotated[
        Path, typer.Option(help="The input excel whit items to process.")
    ],
    out_path: Annotated[
        Path, typer.Option(help="The output folder for processed imx and excel report.")
    ],
):
    validate_process_input(imx_input, excel_input, out_path)
    process_imx_revisions(imx_input, excel_input, out_path)


@app.callback()
def main(verbose: bool = False, debug: bool = False):
    """
    Awesome ImxInsights CLI app.
    """
    if verbose:
        print("[blue]Verbose mode enabled[/blue]")
        state["verbose"] = True

    if debug:
        print("[blue]Debug mode enabled[/blue]")
        state["debug"] = True


if __name__ == "__main__":
    app()
