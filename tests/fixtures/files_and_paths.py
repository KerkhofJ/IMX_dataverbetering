import pytest

from tests.helpers import sample_path


@pytest.fixture(scope="module")
def issue_list() -> str:
    return sample_path("issuelist.xlsx")


@pytest.fixture(scope="module")
def imx_12_xml_file() -> str:
    return sample_path("O_D_003122_ERTMS_SignalingDesign.xml")


@pytest.fixture(scope="module")
def output_path() -> str:
    return sample_path("output")

