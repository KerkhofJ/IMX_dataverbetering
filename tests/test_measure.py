from imxInsights import ImxContainer, ImxSingleFile

from imxTools.insights.measure import calculate_measurements


def test_measure_imx_container(imx_12_container: str):
    calculate_measurements(ImxContainer(imx_12_container))

def test_measure_imx_single_file(imx_single_xml_file: str):
    # todo: below is typehint protocol failure, we should fix this in imxInsights
    calculate_measurements(ImxSingleFile(imx_single_xml_file).initial_situation)
