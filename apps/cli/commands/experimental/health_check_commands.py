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
            "object_path",
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

    revision_list = [
        "ObjectPath",
        "ObjectPuic",
        "IssueComment",
        "IssueCause",
        "AtributeOrElement",
        "Operation",
        "ValueOld",
        "ValueNew",
        "ProcessingStatus",
        "RevisionReasoning"
    ]

    columns_to_copy = ["object_path", "object_puic", "imx_measure", "calculated_3d_measure"]
    new_names = ["ObjectPath", "ObjectPuic", "ValueOld", "ValueNew"]

    df_subset = df[columns_to_copy].copy()
    df_subset.columns = new_names


    for col in revision_list:
        if col not in df_subset.columns:
            df_subset[col] = None

    df_subset["Operation"] = "UpdateAttribute"
    df_subset["AtributeOrElement"] = df["ref_field"].apply(lambda val: val.replace("@railConnectionRef", "@atMeasure") if isinstance(val, str) else val)
    df_subset = df_subset[revision_list]

    # df.to_excel(output_path / "measure_check.xlsx", index=False, sheet_name="measure_check")
    # df_subset.to_excel(output_path / "measure_check.xlsx", index=False, sheet_name="issue_list")

    df_merged = pd.concat([df, df_subset], axis=1)
    df_merged.to_excel(output_path / "measure_check.xlsx", index=False, sheet_name="measure_check")
