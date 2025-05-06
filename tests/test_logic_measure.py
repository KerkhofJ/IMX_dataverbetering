from imxInsights import ImxContainer

from imxTools.insights.measure import calculate_measurements


def test_measure_imx_12(imx_12_container: str):
    calculate_measurements(ImxContainer(imx_12_container))
