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
        imx_12_container: str = typer.Argument(...),
        output_path: Path | None = typer.Option(
            None,
            "--out-path",
            "-o",
            exists=False,
            writable=True,
            help="Directory where the output files will be generated (defaults to cwd)",
        )
):
    out_list = calculate_measurements(ImxContainer(imx_12_container))
    df = pd.DataFrame(
            out_list,
            columns=[
                "object_puic", "ref_field", "ref_field_value", "imx_measure",
                "calculated_3d_measure", "calculated_2d_measure"
            ]
        )
    df.to_excel(output_path/"measure_check.xlsx", index=False)