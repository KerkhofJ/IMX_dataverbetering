import shutil
from pathlib import Path

from typer.testing import CliRunner

from apps.cli.cliApp import app

runner = CliRunner()


def test_comments_command_help():
    result = runner.invoke(app, ["experimental", "comments", "--help"])
    assert result.exit_code == 0
    assert "extract" in result.output
    assert "reproject" in result.output


def test_extract_creates_output(diff_report, clean_output_path):
    out_path = Path(f"{clean_output_path}/extracted_comments.xlsx")
    result = runner.invoke(
        app,
        [
            "experimental",
            "comments",
            "extract",
            diff_report,
            "--out",
            str(out_path),
            "--overwrite",
        ],
    )
    assert result.exit_code == 0
    assert out_path.exists()


def test_extract_with_add_to_wb(diff_report, clean_output_path):
    working_diff_report = Path(clean_output_path) / "working_diff_report.xlsx"
    shutil.copyfile(diff_report, working_diff_report)
    result = runner.invoke(
        app,
        [
            "experimental",
            "comments",
            "extract",
            f"{working_diff_report}",
            "--out",
            f"{clean_output_path}/combined-added.xlsx",
            "--add-to-wb",
            "--overwrite",
        ],
    )
    working_diff_report.unlink()

    assert result.exit_code == 0
    out_path = Path(f"{clean_output_path}/combined-added.xlsx")
    assert out_path.exists()


def test_reproject_applies_comments(diff_report_edit, comment_list, clean_output_path):
    out_path = f"{clean_output_path}/updated_diff_with_comments.xlsx"
    result = runner.invoke(
        app,
        [
            "experimental",
            "comments",
            "reproject",
            diff_report_edit,
            "--comment-list",
            comment_list,
            "--out",
            str(out_path),
        ],
    )
    assert result.exit_code == 0

    out_path = Path(f"{clean_output_path}/updated_diff_with_comments.xlsx")
    assert out_path.exists()
