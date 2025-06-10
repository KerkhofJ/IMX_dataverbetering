from pathlib import Path

from typer.testing import CliRunner

from apps.cli.main import app

runner = CliRunner()


def test_health_check_help_command():
    result = runner.invoke(app, ["health-check", "--help"])
    assert result.exit_code == 0


def test_health_check_measurement_help_command():
    result = runner.invoke(app, ["health-check", "measure", "--help"])
    assert result.exit_code == 0


def test_health_check_measurement_command(
    clean_output_path: str, imx_12_container: str
):
    output_path = Path(clean_output_path) / "measure_check.xlsx"
    result = runner.invoke(
        app,
        [
            "health-check",
            "measure",
            imx_12_container,
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0
    assert output_path.exists()
