from pathlib import Path

import typer
from imxInsights.file.singleFileImx.imxSituationEnum import ImxSituationEnum

from apps.cli.exception_handler import handle_exceptions
from imxTools.insights.measure_analyse import generate_measure_excel
from imxTools.utils.helpers import load_imxinsights_container_or_file

app = typer.Typer()


@handle_exceptions
@app.command()
def measure(
    imx_container: Path = typer.Argument(
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
    t1_situation: ImxSituationEnum | None = typer.Option(
        None,
        "--t1-situation",
        "-s1",
        help="Situation type for IMX T1 (only needed for single imx files)",
    ),
    threshold: float | None = typer.Option(
        None,
        "--threshold",
        "-t",
        help="Threshold for IMX-calculated measure values; if this value is exceeded, it will trigger a correction issue",
    ),
):
    """
    Calculate measurements for IMX files and store them in an Excel file.
    """
    imx = load_imxinsights_container_or_file(imx_container, t1_situation)
    output_path = Path(output_path) if output_path else Path.cwd()
    if threshold:
        generate_measure_excel(imx, output_path, threshold)
    else:
        generate_measure_excel(imx, output_path)
    typer.echo(f"✔ Measurement check Excel written to: {output_path}")
