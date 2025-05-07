from pathlib import Path

import pandas as pd
import typer
from imxInsights import ImxContainer

from apps.cli.exception_handler import handle_exceptions
from imxTools.insights.measure import generate_measurement_dfs

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
    Calculate measurements for IMX files and store them in an Excel file.

    **!! WARNING: THIS IS AN EXPERIMENTAL FEATURE!**

    Current version only works for IMX container (zip files).
    """
    # TODO: make sure we support imx 1.2.4 files include option to give a situation type. encapsulate the to util helper.
    imx = ImxContainer(imx_12_zip)
    df, df_issue_list = generate_measurement_dfs(imx)

    # TODO: we should have a output parameter in the command
    # TODO: this could be a methode in measure methode.
    output_file = output_path / "measure_check.xlsx"
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="measure_check")
        df_issue_list.to_excel(writer, index=False, sheet_name="issue_list")

    typer.echo(f"✔ Measurement check Excel written to: {output_file}")
