from pathlib import Path

import pytest

from imxTools.revision.input_validation import validate_gml_coordinates
from imxTools.revision.process_revision import process_imx_revisions
from imxTools.revision.revision_enums import RevisionColumns
from imxTools.revision.revision_template import get_revision_template


def test_process(issue_list: str, imx_12_xml_file: str, clean_output_path: str):
    df = process_imx_revisions(imx_12_xml_file, issue_list, clean_output_path)
    filtered_df = df[df[RevisionColumns.will_be_processed.name]]
    unique_statuses = filtered_df["status"].unique().tolist()
    assert len(unique_statuses) == 1 and unique_statuses[0] == "processed", (
        "should all be processed"
    )


def test_get_template(clean_output_path: str):
    out_path = Path(clean_output_path) / "template.xlsx"
    get_revision_template(out_path)
    assert out_path.exists()
    # todo: should test if sheet and all columns are present


@pytest.mark.parametrize(
    "valid_input",
    [
        "32560.034,391253.849",  # 2D Point
        "32560.034,391253.849,2.606",  # 3D Point
        "174581.147,448873.584 174606.19,448866.162",  # 2D LineString
        "1.0,2.0,3.0 4.0,5.0,6.0 7.0,8.0,9.0",  # 3D LineString
        "-123.456,-789.012",  # 2D negative Point
        "-1.1,-2.2,-3.3 -4.4,-5.5,-6.6",  # 3D LineString with negatives
    ],
)
def test_valid_coordinates(valid_input):
    assert validate_gml_coordinates(valid_input) is True


@pytest.mark.parametrize(
    "invalid_input",
    [
        "211586.818, 473917.758 211585.069, 473917.657 211416.896, 473906.921",  # line whit spacee
        "",  # Empty string
        " ",  # Space only
        "32560.034 ,391253.849",  # Space before comma
        "32560.034, 391253.849",  # Space after comma
        " 32560.034,391253.849",  # Leading space
        "32560.034,391253.849 ",  # Trailing space
        "1.0,2.0 3.0,4.0,5.0",  # Mixed 2D/3D
        "1.0,2.0 3.0,4.0,5.0 6.0,7.0",  # Mixed dimensions
        "1.0,2.0,,3.0",  # Malformed comma
        "1.0,2.0  3.0,4.0",  # Double space
        "1.0,2.0,3.0,4.0",  # Too many components
        "1.0,2.0,3.0 ",  # Trailing space
        "-1.0,-2.0 -3.0,4.0,5.0,6.0",  # 2D + invalid 4D
    ],
)
def test_invalid_coordinates(invalid_input):
    assert validate_gml_coordinates(invalid_input) is False
