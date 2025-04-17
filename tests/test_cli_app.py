from pathlib import Path

from typer.testing import CliRunner

from imxCli.cliApp.cliApp import app
from utils.helpers import clear_directory

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


def test_revision_template():
    clear_directory(Path("output"))

    # valid run
    result = runner.invoke(
        app,
        [
            "revision-template",
            "--out-path", "output/template.xlsx",
        ],
    )
    assert result.exit_code == 0

    # file exist
    result = runner.invoke(
        app,
        [
            "revision-template",
            "--out-path", "output/template.xlsx",
        ],
    )
    assert result.exit_code == 1

    # file not excel
    result = runner.invoke(
        app,
        [
            "revision-template",
            "--out-path", "output/template.xl",
        ],
    )
    assert result.exit_code == 1


def test_process_command():

    # clean output dir
    clear_directory(Path("output"))

    # valid run
    result = runner.invoke(
        app,
        [
            "revision",
            "--imx-input", "data/O_D_003122_ERTMS_SignalingDesign.xml",
            "--excel-input", "data/issuelist.xlsx",
            "--out-path", "output",
        ],
    )
    assert result.exit_code == 0

    # output exist
    result = runner.invoke(
        app,
        [
            "revision",
            "--imx-input", "data/O_D_003122_ERTMS_SignalingDesign.xml",
            "--excel-input", "data/issuelist.xlsx",
            "--out-path", "output",
        ],
    )
    assert result.exit_code == 1

    # imx-input not present
    result = runner.invoke(
        app,
        [
            "revision",
            "--imx-input", "data/123.xml",
            "--excel-input", "data/issuelist.xlsx",
            "--out-path", "output",
        ],
    )
    assert result.exit_code == 1

    # excel-input not present
    result = runner.invoke(
        app,
        [
            "revision",
            "--imx-input", "data/O_D_003122_ERTMS_SignalingDesign.xml",
            "--excel-input", "data/123.xlsx",
            "--out-path", "output",
        ],
    )
    assert result.exit_code == 1


