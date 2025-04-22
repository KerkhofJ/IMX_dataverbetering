import pytest

from pathlib import Path

from typer.testing import CliRunner

from imxTools.cliApp.cliApp import app
from imxTools.utils.helpers import clear_directory

runner = CliRunner()


def test_general_help_command():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_revision_help_command():
    result = runner.invoke(app, ["revision", "--help"])
    assert result.exit_code == 0


def test_revision_template_help_command():
    result = runner.invoke(app, ["revision-template", "--help"])
    assert result.exit_code == 0


def test_revision_template(output_path: str):
    clear_directory(Path(output_path))

    # valid run
    result = runner.invoke(
        app,
        [
            "revision-template",
            f"{output_path}/template.xlsx",
        ],
    )
    assert result.exit_code == 0, "Should create a template file"

    # file exist
    result = runner.invoke(
        app,
        [
            "revision-template",
            f"{output_path}/template.xlsx",
        ],
    )
    assert result.exit_code == 1, "Should not create template file if file exists"

    # file not excel
    result = runner.invoke(
        app,
        [
            "revision-template",
            f"{output_path}/template.not_xlsx",
        ],
    )
    assert result.exit_code == 1, "Should not create template file if file is not .xlsx or xlsm"




def test_process_command(issue_list: str, imx_12_xml_file: str, output_path: str):

    # clean output dir
    clear_directory(Path(output_path))

    # valid run
    result = runner.invoke(
        app,
        [
            "revision",
            imx_12_xml_file,
            issue_list,
            output_path,
        ],
    )
    assert result.exit_code == 0, "Should create processed imx and excel log"

    # output exist
    result = runner.invoke(
        app,
        [
            "revision",
            imx_12_xml_file,
            issue_list,
            output_path,
        ],
    )
    assert result.exit_code == 1, "Should not create processed imx and excel log if output exist"

    # imx-input not present
    result = runner.invoke(
        app,
        [
            "revision",
            "data/123.xml",
            issue_list,
            output_path
        ],
    )
    assert result.exit_code == 1, "Should not create processed imx and excel log if input imx not present"

    # excel-input not present
    result = runner.invoke(
        app,
        [
            "revision",
            imx_12_xml_file,
            "data/123.xlsx",
            output_path,
        ],
    )
    assert result.exit_code == 1, "Should not create processed imx and excel log if input excel not present"
