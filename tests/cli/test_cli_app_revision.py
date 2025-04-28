from pathlib import Path

import pytest
from typer.testing import CliRunner

from apps.cli.cliApp import app
from imxTools.utils.helpers import clear_directory

runner = CliRunner()


# Help command tests
def test_revision_command_help():
    result = runner.invoke(app, ["revision", "--help"])
    assert result.exit_code == 0


def test_revision_apply_command_help():
    result = runner.invoke(app, ["revision", "apply", "--help"])
    assert result.exit_code == 0


def test_revision_template_command_help():
    result = runner.invoke(app, ["revision", "template", "--help"])
    assert result.exit_code == 0


# Template command tests
def test_revision_template_creates_file(clean_output_path: str):
    result = runner.invoke(
        app, ["revision", "template", "--out-path", f"{clean_output_path}"]
    )
    assert result.exit_code == 0, "Should create a template file"



def test_revision_template_fails_if_file_exists(clean_output_path: str):
    clean_output_path = Path(clean_output_path)
    runner.invoke(app, ["revision", "template", "--out-path", clean_output_path])
    result = runner.invoke(app, ["revision", "template", clean_output_path])
    assert result.exit_code == 1, "Should not create template file if file exists"


def test_revision_apply_valid_run(
    issue_list: str, imx_12_xml_file: str, clean_output_path: str
):
    result = runner.invoke(
        app, ["revision", "apply", imx_12_xml_file, issue_list, "--out-path", clean_output_path]
    )
    assert result.exit_code == 0, "Should create processed IMX and Excel log"


def test_revision_apply_fails_if_output_exists(
    issue_list: str, imx_12_xml_file: str, clean_output_path: str
):
    runner.invoke(app, ["revision", "apply", imx_12_xml_file, issue_list, "--out-path", clean_output_path])
    result = runner.invoke(
        app, ["revision", "apply", imx_12_xml_file, issue_list, "--out-path",  clean_output_path]
    )
    assert result.exit_code == 1, "Should not create processed files if output exists"


def test_revision_apply_fails_if_imx_missing(issue_list: str, clean_output_path: str):
    result = runner.invoke(
        app, ["revision", "apply", "data/123.xml", issue_list, "--out-path", clean_output_path]
    )
    assert result.exit_code == 1, "Should not process if input IMX file is missing"


def test_revision_apply_fails_if_excel_missing(imx_12_xml_file: str, clean_output_path: str):
    result = runner.invoke(
        app, ["revision", "apply", imx_12_xml_file, "data/123.xlsx", "--out-path", clean_output_path]
    )
    assert result.exit_code == 1, "Should not process if input Excel file is missing"
