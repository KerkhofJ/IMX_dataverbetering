from imxTools.xml.kilometer_ribbon import add_km_to_imx_xml_file




# def add_km(imx_12_xml_file: str, output_path: str):
def add_km():
    add_km_to_imx_xml_file(
        r"C:\repos\IMX_dataverbetering\sample_data\imx_12_xml_file.xml",
        r"C:\repos\IMX_dataverbetering\sample_data\output\test.xml"
    )


add_km()