from pathlib import Path
from typing import Annotated

import typer
from rich import print

from imxCli.cliApp.exception_handler import handle_input_validation
from imxCli.revision.process_revision import process_imx_revisions
from imxCli.revision.revision_template import get_revision_template
from imxCli.utils.input_validation import validate_process_input

app = typer.Typer()

state = {
    "verbose": False,
    "debug": False,
}


@handle_input_validation
@app.command()
def diff():
    # TODO: create diff cli command
    pass


@handle_input_validation
@app.command()
def geojsons():
    # TODO: create geojson cli command
    pass


@handle_input_validation
@app.command()
def create_manifest():
    # TODO: create manifest cli command
    pass


@handle_input_validation
@app.command()
def validate_manifest():
    # TODO: validate manifest cli command
    pass


@handle_input_validation
@app.command()
def add_km_manifest():
    # TODO: add km to imx cli command
    pass


@handle_input_validation
@app.command()
def extract_comments():
    # TODO: create excel sheet / file of all comments in diff or population report
    pass


@handle_input_validation
@app.command()
def revision_template(
    out_path: Annotated[
        Path,
        typer.Option(help="Directory where the revision Excel template will be saved."),
    ],
):
    """
    This command generates a revision Excel template to a given directory.
    """
    if out_path.suffix not in {".xlsx", ".xlsm"}:
        raise ValueError("Path is not a excel file")
    if out_path.exists():
        raise ValueError("File all ready exist!")
    get_revision_template(out_path)


@handle_input_validation
@app.command()
def revision(
    imx_input: Annotated[Path, typer.Option(help="The input imx file as a xml file.")],
    excel_input: Annotated[
        Path, typer.Option(help="The input excel whit revision items to process.")
    ],
    out_path: Annotated[
        Path, typer.Option(help="The output folder for processed imx and excel report.")
    ],
):
    """
    Applies modifications to an IMX file based on a provided Excel file.

    The Excel file should follow a specific format, which can be generated using the `revision_template` command.
    The modified IMX file, along with a corresponding report, will be saved to the specified output directory.
    """
    validate_process_input(imx_input, excel_input, out_path)
    process_imx_revisions(imx_input, excel_input, out_path)


@app.callback()
def main(verbose: bool = False, debug: bool = False):
    """
    Awesome open-imx.nl CLI app.
    """
    if verbose:
        print("[blue]Verbose mode enabled[/blue]")
        state["verbose"] = True

    if debug:
        print("[blue]Debug mode enabled[/blue]")
        state["debug"] = True


if __name__ == "__main__":
    app()
