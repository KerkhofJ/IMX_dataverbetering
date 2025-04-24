from pathlib import Path
from typing import Annotated

import typer

from imxTools.cliApp.exception_handler import handle_exceptions
from imxTools.revision.input_validation import validate_process_input
from imxTools.revision.process_revision import process_imx_revisions
from imxTools.revision.revision_template import get_revision_template

app = typer.Typer()


@handle_exceptions
@app.command()
def template(
    out_path: Annotated[
        Path,
        typer.Argument(help="Path to the revision Excel template to create (.xlsx)."),
    ],
):
    """
    Generate a (example filled) Excel template for performing IMX revisions.

    This command creates an Excel file that can be used to define revisions
    to an IMX file. The structure of this template must be followed when
    preparing data for the `revision` command.

    - The file must not already exist.
    - The output path must end with `.xlsx`.

    Example:
        python app.py revision-template ./revision_template.xlsx
    """
    if out_path.suffix != ".xlsx":
        raise ValueError("Path must be an Excel file with .xlsx extension.")
    if out_path.exists():
        raise ValueError("File already exists!")
    get_revision_template(out_path)


@handle_exceptions
@app.command()
def apply(
    imx_input: Annotated[Path, typer.Argument(help="The input IMX file (.xml).")],
    excel_input: Annotated[
        Path, typer.Argument(help="The Excel file with revision items.")
    ],
    out_path: Annotated[
        Path,
        typer.Argument(help="The output folder for modified IMX and Excel report."),
    ],
):
    """
    Apply revisions to an IMX file using a structured Excel file.

    This command reads an IMX file and applies updates based on revision instructions
    found in an accompanying Excel file. A new IMX file and a detailed Excel report
    are written to the given output folder.

    The Excel file must follow the format provided by the `revision-template` command.

    Example:
        python app.py revision input.imx.xml revisions.xlsx ./output
    """
    validate_process_input(imx_input, excel_input, out_path)
    process_imx_revisions(imx_input, excel_input, out_path)


@handle_exceptions
@app.command()
def extract_comments():
    # TODO: create excel sheet / file of all comments in diff or population report
    pass
