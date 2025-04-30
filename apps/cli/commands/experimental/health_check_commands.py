from pathlib import Path

import pandas as pd
import typer
from imxInsights import ImxContainer

from apps.cli.exception_handler import handle_exceptions
from imxTools.insights.measure import calculate_measurements

app = typer.Typer()


@handle_exceptions
@app.command()
def measure_check(
    imx_12_zip: str = typer.Argument(..., help="Path to the input imx12 zip."),
    output_path: Path = typer.Option(
        Path.cwd(),
        "--out-path",
        "-o",
        exists=False,
        writable=True,
        help="Directory where the output files will be generated (defaults to cwd)",
    ),
):
    """
    Calculate measurements for IMX files and stores them in an Excel file.

    **!! WARNING: THIS IS AN EXPERIMENTAL FEATURE!**

    Current version only works for imx12 zip files.
    """
    out_list = calculate_measurements(ImxContainer(imx_12_zip))
    df = pd.DataFrame(
        out_list,
        columns=[
            "object_puic",
            "object-name",
            "ref_field",
            "ref_field_value",
            "ref_field_name",
            "imx_measure",
            "calculated_3d_measure",
            "3d diff distance",
            "calculated_2d_measure",
            "2d diff distance",
        ],
    )
    df.to_excel(output_path / "measure_check.xlsx", index=False)
