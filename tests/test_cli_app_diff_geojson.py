import glob
import os

import pytest

from pathlib import Path
from typer.testing import CliRunner

from imxTools.cliApp.cliApp import app


runner = CliRunner()


def test_diff_help_command():
    result = runner.invoke(app, ["diff", "--help"])
    assert result.exit_code == 0


def _assert_dif_present(path: str) -> None:
    pattern = os.path.join(path, '*-diff.xlsx')
    matching_files = glob.glob(pattern)
    assert matching_files, f"No file found matching the pattern {pattern}"


def test_diff_geojson_enabled(clean_output_path: str, imx_12_container: str):
    result = runner.invoke(
        app,
        [
            "diff",
            imx_12_container,
            imx_12_container,
            clean_output_path,
            "--geojson",
            "--wgs",
        ],
    )
    assert result.exit_code == 0
    _assert_dif_present(clean_output_path)

    pattern = os.path.join(clean_output_path, '*-geojsons')
    matching_folders = glob.glob(pattern)
    assert matching_folders, f"No folder found matching the pattern {pattern}"

    assert any(Path(matching_folders[0]).iterdir())



def test_diff_geojson_disabled(clean_output_path: str, imx_12_container: str):
    result = runner.invoke(
        app,
        [
            "diff",
            imx_12_container,
            imx_12_container,
            clean_output_path,
        ],
    )
    assert result.exit_code == 0
    _assert_dif_present(clean_output_path)

    assert not Path(clean_output_path, "geojsons").exists()


def test_diff_with_t2_situation(clean_output_path: str, imx_12_container: str, imx_single_xml_file: str):
    result = runner.invoke(
        app,
        [
            "diff",
            imx_12_container,
            imx_single_xml_file,
            clean_output_path,
            "--t2-situation", "InitialSituation",
        ],
    )
    assert result.exit_code == 0
    _assert_dif_present(clean_output_path)
    assert not Path(clean_output_path, "geojsons").exists()


def test_diff_with_t1_situation(clean_output_path: str, imx_12_container: str, imx_single_xml_file: str):
    result = runner.invoke(
        app,
        [
            "diff",
            imx_single_xml_file,
            imx_12_container,
            clean_output_path,
            "--t1-situation", "InitialSituation",
        ],
    )
    assert result.exit_code == 0
    _assert_dif_present(clean_output_path)
    assert not Path(clean_output_path, "geojsons").exists()


def test_diff_with_matching_situations(clean_output_path: str, imx_single_xml_file: str):
    result = runner.invoke(
        app,
        [
            "diff",
            imx_single_xml_file,
            imx_single_xml_file,
            clean_output_path,
            "--t1-situation", "InitialSituation",
            "--t2-situation", "InitialSituation",
        ],
    )
    assert result.exit_code == 0
    _assert_dif_present(clean_output_path)
    assert not Path(clean_output_path, "geojsons").exists()


def test_diff_with_mismatched_situations(clean_output_path: str, imx_single_xml_file: str):
    result = runner.invoke(
        app,
        [
            "diff",
            imx_single_xml_file,
            imx_single_xml_file,
            clean_output_path,
            "--t1-situation", "InitialSituation",
            "--t2-situation", "NewSituation",
        ],
    )
    assert result.exit_code == 1
    assert result.exception.args[0] == 'IMX T2 results in None. Is the situation present in the IMX file?'
