from pathlib import Path

import pytest

from imxTools.utils.helpers import clear_directory
from tests.helpers import sample_path


@pytest.fixture(scope="module")
def issue_list() -> str:
    return sample_path("issuelist.xlsx")


@pytest.fixture(scope="module")
def imx_12_xml_file() -> str:
    return sample_path("imx_12_xml_file.xml")


@pytest.fixture(scope="module")
def output_path() -> str:
    return sample_path("output")


@pytest.fixture
def clean_output_path(output_path: str):
    # This fixture yields the output path and ensures cleanup afterward
    yield output_path
    # clear_directory(Path(output_path))


@pytest.fixture(scope="module")
def imx_12_container() -> str:
    return sample_path("imx_12_container.zip")


@pytest.fixture(scope="module")
def imx_12_container_folder() -> str:
    return sample_path("imx_12_container_folder")


@pytest.fixture(scope="module")
def imx_single_xml_file() -> str:
    return sample_path("imx_124_single_file.xml")

@pytest.fixture(scope="module")
def diff_report() -> str:
    return sample_path("20250430_202130-diff.xlsx")


@pytest.fixture(scope="module")
def diff_report_edit() -> str:
    return sample_path("20250430_202130-diff-edit.xlsx")


@pytest.fixture(scope="module")
def comment_list() -> str:
    return sample_path("comment-list.xlsx")
