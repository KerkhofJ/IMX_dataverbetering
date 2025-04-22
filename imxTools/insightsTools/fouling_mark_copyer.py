from pathlib import Path
import xmlschema
from lxml import etree

NAMESPACE = "http://www.prorail.nl/IMSpoor"


#TODO: this is generic, should move to helpers.
def load_imx_file(file_path: Path):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(str(file_path), parser=parser)
    return tree.getroot()


def get_fouling_points(root, situation_tag: str):
    situation_element = root.find(f'*{{{NAMESPACE}}}{situation_tag}')
    return situation_element.findall(f'.//{{{NAMESPACE}}}FoulingPoint')


def create_parent_element_mapping(fouling_points):
    parent_dict = {}
    for item in fouling_points:
        parent = item.getparent()
        parent_puic = parent.get("puic")
        parent_dict.setdefault(parent_puic, []).append(item)
    return parent_dict


def add_fouling_marks_and_validate(parent_dict, root_container, xsd_schema):
    all_xsd_errors = []
    for key, items in parent_dict.items():
        matching_elements = list(root_container.findall(f'.//*[@puic="{key}"]'))
        if len(matching_elements) != 1:
            raise ValueError(f"Found no or more than one element with PUIC {key}")

        matching_element = matching_elements[0]
        switch_blades = matching_element.findall(f'.//{{{NAMESPACE}}}SwitchBlades')

        if switch_blades:
            last_blade = switch_blades[-1]
            for item in items:
                item.tag = "FoulingMark"
                last_blade.addnext(item)

        xml_bytes = etree.tostring(matching_element)
        errors = list(xsd_schema.iter_errors(xml_bytes))
        if errors:
            all_xsd_errors.extend(errors)

    return all_xsd_errors


def copy_fooling_marks(
    xsd_path: Path,
    imx_file: Path,
    situation_tag: str,
    container_file: Path,
    output_file: Path
) -> list:
    """
    Process an IMX file to insert FoulingMarks and validate it against the XSD.

    Returns a list of XSD validation errors.
    """
    xsd_schema = xmlschema.XMLSchema(str(xsd_path))
    root = load_imx_file(imx_file)
    root_container = load_imx_file(container_file)

    fouling_points = get_fouling_points(root, situation_tag)
    parent_dict = create_parent_element_mapping(fouling_points)

    xsd_errors = add_fouling_marks_and_validate(parent_dict, root_container, xsd_schema)

    with open(output_file, 'wb') as f:
        etree.ElementTree(root_container).write(f, pretty_print=True, xml_declaration=True, encoding='UTF-8')

    return xsd_errors
