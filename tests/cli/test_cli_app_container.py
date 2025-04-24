import pytest

import zipfile
from pathlib import Path
from typer.testing import CliRunner

from imxTools.cliApp.cliApp import app


runner = CliRunner()


def _find_new_zip_file(before: set[Path], after: set[Path]) -> Path:
    new_files = after - before
    assert new_files, "No new ZIP file was created"
    return new_files.pop()


def test_container_help_command():
    result = runner.invoke(app, ["container", "--help"])
    assert result.exit_code == 0


def test_create_container_help_command():
    result = runner.invoke(app, ["container", "generate", "--help"])
    assert result.exit_code == 0


def test_create_container_command(imx_12_container: str, clean_output_path: str):
    output_path = Path(clean_output_path)
    before = set(output_path.glob("*.zip"))

    result = runner.invoke(app, ["container", "generate", imx_12_container, clean_output_path])
    assert result.exit_code == 0

    after = set(output_path.glob("*.zip"))
    zip_file = _find_new_zip_file(before, after)
    assert zipfile.is_zipfile(zip_file)


def test_create_container_command_no_output(imx_12_container: str, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    before = set(tmp_path.glob("*.zip"))

    result = runner.invoke(app, ["container", "generate", imx_12_container])
    assert result.exit_code == 0

    after = set(tmp_path.glob("*.zip"))
    zip_file = _find_new_zip_file(before, after)
    assert zipfile.is_zipfile(zip_file)
    zip_file.unlink()


def test_create_manifest_command(imx_12_container: str, clean_output_path: str):
    output_path = Path(clean_output_path)
    manifest_path = output_path / "manifest.xml"

    result = runner.invoke(app, ["container", "generate", imx_12_container, clean_output_path, "--manifest"])
    assert result.exit_code == 0

    assert manifest_path.exists(), "Manifest file was not created"
    assert manifest_path.read_text().strip().startswith("<")


def test_create_manifest_command_no_output(imx_12_container: str, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    manifest_path = tmp_path / "manifest.xml"

    result = runner.invoke(app, ["container", "generate", imx_12_container, "--manifest"])
    assert result.exit_code == 0

    assert manifest_path.exists(), "Manifest file was not created in cwd"
    assert manifest_path.read_text().strip().startswith("<")
    manifest_path.unlink()
