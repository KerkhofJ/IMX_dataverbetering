from pathlib import Path

import typer
from imxInsights.file.singleFileImx.imxSituationEnum import ImxSituationEnum

from apps.cli.exception_handler import handle_exceptions
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
    output_path: Path | None = typer.Option(
        None,
        "--out-path",
        "-o",
        exists=False,
        writable=True,
        help="Directory where the output files will be generated (defaults to cwd)",
    ),
    t1_situation: ImxSituationEnum | None = typer.Option(
        None,
        "--t1-situation",
        "-s1",
        help="Situation type for IMX T1 (only needed for single imx files)",
    ),
    t2_situation: ImxSituationEnum | None = typer.Option(
        None,
        "--t2-situation",
        "-s2",
        help="Situation type for IMX T2 (only needed for single imx files)",
    ),
    geojson: bool = typer.Option(
        False, "--geojson", "-g", help="Include generating a GeoJSON diff folder"
    ),
    to_wgs: bool = typer.Option(
        False, "--wgs84", "-wgs", help="Geojson CRS WGS84 (else RD + NAP EPSG:7415)"
    ),
):
    """
    Compare two IMX containers and generate a diff report.

    This command compares two single IMX XML files or zip containers and generates an
    Excel report with the differences. Optionally, it can also export changes as GeoJSON files.
    \n\n
    - For a single imx file you must include a valid IMX situation.\n
    - If both inputs are the same file, you must specify both input files and different situations.\n
    - Different IMX version are acceptable; however, they may lead to difficult-to-track changes.\n
    \n
    The generated output is timestamped and saved to the given output path.
    \n\n
    This feature relies on imxInsights (https://pypi.org/project/imxInsights/) to handle the heavy lifting.
    """
    write_diff_output_files(
        t1_path, t2_path, output_path, t1_situation, t2_situation, geojson, to_wgs
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
    output_path: Path | None = typer.Option(
        None,
        "--out-path",
        "-o",
        exists=False,
        writable=True,
        help="Directory where the output files will be generated (defaults to cwd)",
    ),
    imx_situation: ImxSituationEnum | None = typer.Option(
        None, help="Situation type for IMX (only needed for single imx files)"
    ),
    geojson: bool = typer.Option(
        False, "--geojson", "-g", help="Include generating a GeoJSON diff folder"
    ),
    to_wgs: bool = typer.Option(
        False, "--wgs84", "-wgs", help="Geojson CRS WGS84 (else RD + NAP EPSG:7415)"
    ),
):
    """
    Generate a population report from a IMX container.
    \n\n
    This command reads a single IMX XML file or zip container, and generates a population report in Excel format.
    Optionally, it can also export GeoJSON files representing the dataset.
    \n\n
    - For a single imx file you must include a valid IMX situation.\n
    - The output files are saved to the specified output path with a timestamp.
    \n\n
    This  feature relies on imxInsights (https://pypi.org/project/imxInsights/) to handle the heavy lifting.
    """
    write_population_output_files(imx, output_path, imx_situation, geojson, to_wgs)


# @handle_exceptions
# @app.command()
# def compare_chain():
#     pass
