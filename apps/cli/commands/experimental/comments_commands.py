from pathlib import Path

import typer

from apps.cli.exception_handler import handle_exceptions
from imxTools.comments.comments_extractor import extract_comments_to_new_sheet
from imxTools.comments.comments_replacer import apply_comments_from_issue_list

app = typer.Typer()


@handle_exceptions
@app.command()
def extract(
    input_path: Path = typer.Argument(
        ..., help="Path to the input diff report Excel file."
    ),
    output_path: Path = typer.Option(
        ...,
        "--out",
        "-o",
        help="Output Excel file path to save the extracted comments.",
    ),
    add_to_wb: bool = typer.Option(
        False,
        "--add-to-wb",
        help="Add comments to the existing workbook as a new sheet.",
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite the output file if it exists."
    ),
):
    """
    Extracts comments from the diff report and saves them to a new sheet or workbook.
    """
    extract_comments_to_new_sheet(
        input_path,
        str(output_path),
        add_to_wb=add_to_wb,
        overwrite=overwrite,
    )


@handle_exceptions
@app.command()
def reproject(
    input_path: Path = typer.Argument(
        ..., help="Path to the new diff report Excel file to apply comments to."
    ),
    comment_list: Path = typer.Option(
        ...,
        "--comment-list",
        "-c",
        help="Path to the Excel file with extracted comments.",
    ),
    output_path: Path = typer.Option(
        ..., "--out", "-o", help="Path to the output Excel file with applied comments."
    ),
):
    """
    Applies comments from a comment list to a new diff report and saves the result.
    """
    apply_comments_from_issue_list(
        issue_list_path=comment_list,
        new_diff_path=input_path,
        output_path=str(output_path),
    )


if __name__ == "__main__":
    app()
