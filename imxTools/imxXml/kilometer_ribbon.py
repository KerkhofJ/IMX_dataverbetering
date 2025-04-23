from imxInsights import ImxContainer
from kmService import KmService, get_km_service
from lxml import etree
from shapely import Point

KM_SERVICE: KmService | None = None


def add_km_to_imx_xml_file(imx_file_path: str, output_file: str):
    global KM_SERVICE

    if KM_SERVICE is None:
        KM_SERVICE = get_km_service()

    imx_container = ImxContainer(imx_file_path)

    all_objects = list(imx_container.get_all())
    used_lints = []

    for imx_object in all_objects:
        if isinstance(imx_object.geometry, Point):
            result = KM_SERVICE.get_km(imx_object.geometry.x, imx_object.geometry.y)
            location_xml_string = result.imx_ribbon_locations()
            location_xml = etree.fromstring(location_xml_string)

            geo_location_node = imx_object.element.find(
                ".//{http://www.prorail.nl/IMSpoor}GeographicLocation"
            )
            if geo_location_node is not None:
                parent = geo_location_node.getparent()
                index = parent.index(geo_location_node)
                parent.insert(index + 1, location_xml)
                parent.insert(
                    index + 1,
                    etree.Comment(
                        f"KmValue {result.display} added by kmService open-imx.nl, see docs for the accuracy disclaimer"
                    ),
                )

            ribbon_xml_ribbon = result.imx_kilometer_ribbons()
            if ribbon_xml_ribbon not in used_lints:
                used_lints.append(ribbon_xml_ribbon)

    km_ribbons_string = (
        '<KilometerRibbons xmlns:gml="http://www.opengis.net/gml">\n'
        + "\n".join(used_lints)
        + "\n</KilometerRibbons>"
    )
    demarcation_node = imx_container.files.signaling_design.root.find(
        ".//{http://www.prorail.nl/IMSpoor}Demarcations"
    )
    parent = demarcation_node.getparent()
    index = parent.index(demarcation_node)
    parent.insert(index + 1, etree.fromstring(km_ribbons_string))

    imx_container.files.signaling_design.root.write(
        output_file, pretty_print=True, xml_declaration=True, encoding="UTF-8"
    )
