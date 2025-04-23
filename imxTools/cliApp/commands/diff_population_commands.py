from pathlib import Path

import typer
from imxInsights.file.singleFileImx.imxSituationEnum import ImxSituationEnum

from imxTools.cliApp.exception_handler import handle_exceptions
from imxTools.insights.diff_and_population import (
    write_diff_output_files,
    write_population_output_files,
)

app = typer.Typer()


@handle_exceptions
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

    This feature relies on imxInsights (https://pypi.org/project/imxInsights/) to handle the heavy lifting.

    Example:
        python app.py diff t1.zip t2.zip ./output --geojson --wgs
    """
    write_diff_output_files(
        t1_path, t2_path, out_path, t1_situation, t2_situation, geojson, to_wgs
    )


@handle_exceptions
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

    This feature relies on imxInsights (https://pypi.org/project/imxInsights/) to handle the heavy lifting.

    Example:
        python app.py population imx.zip ./output --geojson --wgs
    """
    write_population_output_files(imx, out_path, imx_situation, geojson, to_wgs)


@handle_exceptions
@app.command()
def extract_comments():
    # TODO: create excel sheet / file of all comments in diff or population report
    pass
