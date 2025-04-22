from pathlib import Path
from typing import Annotated

import typer
from imxInsights.file.singleFileImx.imxSituationEnum import ImxSituationEnum
from rich import print

from imxTools.cliApp.exception_handler import handle_input_validation
from imxTools.insightsTools.diff_and_population import (
    write_diff_output_files,
    write_population_output_files,
)
from imxTools.revision.input_validation import validate_process_input
from imxTools.revision.process_revision import process_imx_revisions
from imxTools.revision.revision_template import get_revision_template

app = typer.Typer()


state = {
    "verbose": False,
    "debug": False,
}


@handle_input_validation
@app.command()
def diff(
    t1_path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Path to the IMX T1 xml file or zip container",
    ),
    t2_path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Path to the IMX T2 xml file or zip container",
    ),
    out_path: Path = typer.Argument(
        ...,
        exists=False,
        writable=True,
        help="Path where the output files will be generated (should not exists)",
    ),
    t1_situation: ImxSituationEnum | None = typer.Option(
        None, help="Situation type for IMX T1 (only needed for single imx files)"
    ),
    t2_situation: ImxSituationEnum | None = typer.Option(
        None, help="Situation type for IMX T2 (only needed for single imx files)"
    ),
    geojson: bool = typer.Option(
        False, "--geojson", help="Export GeoJSON to output directory"
    ),
    to_wgs: bool = typer.Option(False, "--wgs", help="Geojson in wgs"),
):
    """
    Compare two IMX datasets (T1 and T2) and generate a diff report.

    This command compares two IMX XML files or containers (T1 and T2) and
    generates an Excel report with the differences. Optionally, it can also
    export the geographic changes as GeoJSON files.

    - If the input is a container, it must include a valid IMX situation.
    - If both inputs are the same file, you must specify different situations.

    The generated output is timestamped and saved to the given output path.

    Example:
        python app.py diff t1.zip t2.zip ./output --geojson --wgs
    """
    write_diff_output_files(
        t1_path, t2_path, out_path, t1_situation, t2_situation, geojson, to_wgs
    )


@handle_input_validation
@app.command()
def population(
    imx: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Path to the IMX xml file or zip container",
    ),
    out_path: Path = typer.Argument(
        ...,
        exists=False,
        writable=True,
        help="Path where the output files will be generated (should not exists)",
    ),
    imx_situation: ImxSituationEnum | None = typer.Option(
        None, help="Situation type for IMX (only needed for single imx files)"
    ),
    geojson: bool = typer.Option(
        False, "--geojson", help="Export GeoJSON to output directory"
    ),
    to_wgs: bool = typer.Option(False, "--wgs", help="Geojson in wgs"),
):
    """
    Export population data from a single IMX dataset.

    This command reads a single IMX XML file or zip container, and generates
    a population report in Excel format. Optionally, it can also export
    GeoJSON files representing the dataset.

    - If the input is a container, a specific IMX situation may be required.
    - The output files are saved to the specified output path with a timestamp.

    Example:
        python app.py population imx.zip ./output --geojson --wgs
    """
    write_population_output_files(imx, out_path, imx_situation, geojson, to_wgs)


# @handle_input_validation
# @app.command()
# def create_manifest():
#     # TODO: create manifest cli command
#     pass
#
#
# @handle_input_validation
# @app.command()
# def validate_manifest():
#     # TODO: validate manifest cli command
#     pass
#


# @handle_input_validation
# @app.command()
# def add_km():
#     # TODO: add km to imx cli command
#     pass


# @handle_input_validation
# @app.command()
# def measure_check():
#     # TODO: create measure check excel cli command
#     pass


# @handle_input_validation
# @app.command()
# def extract_comments():
#     # TODO: create excel sheet / file of all comments in diff or population report
#     pass


@handle_input_validation
@app.command()
def revision_template(
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


@handle_input_validation
@app.command()
def revision(
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


@app.callback()
def main(verbose: bool = False, debug: bool = False):
    """
    Open-IMX Command Line Interface (CLI) for managing IMX data.

    This is the main entry point for all Open-IMX CLI commands. It provides
    flexibility to configure the verbosity of logs and enable debug mode.

    - Use the `verbose` flag to get more detailed logging.
    - Use the `debug` flag to enable debug mode for deeper insights.

    Example:
        python app.py --verbose --debug
    """
    if verbose:
        print("[blue]Verbose mode enabled[/blue]")
        state["verbose"] = True

    if debug:
        print("[blue]Debug mode enabled[/blue]")
        state["debug"] = True


if __name__ == "__main__":
    app()
