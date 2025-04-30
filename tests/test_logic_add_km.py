import pytest


from imxTools.xml.kilometer_ribbon import add_km_to_imx_xml_file

# @pytest.mark.slow
def test_add_km(imx_12_container, clean_output_path):
    add_km_to_imx_xml_file(
        imx_12_container,
        clean_output_path
    )
