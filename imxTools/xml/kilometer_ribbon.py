import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Union, Iterable, List

import xmlschema
from imxInsights import ImxContainer
from kmService import KmService, get_km_service
from lxml import etree
from shapely.geometry import Point

from insights.container import create_container

# Namespaces
IMSPOOR_NS = "http://www.prorail.nl/IMSpoor"
GML_NS = "http://www.opengis.net/gml"

# Singleton for KM service
_KM_SERVICE: KmService | None = None

def _get_km_service() -> KmService:
    """Lazily initialize and return the KM service singleton."""
    global _KM_SERVICE
    if _KM_SERVICE is None:
        _KM_SERVICE = get_km_service()
    return _KM_SERVICE


def write_compact_xml(xml_input: Union[etree._Element, etree._ElementTree], path: Path) -> None:
    """
    Serialize an XML element or tree without extra whitespace.
    """
    # Normalize to ElementTree
    if isinstance(xml_input, etree._Element):
        tree = etree.ElementTree(xml_input)
    elif isinstance(xml_input, etree._ElementTree):
        tree = xml_input
    else:
        raise TypeError(f"Expected Element or ElementTree, got {type(xml_input)}")

    # Dump, reparse without blanks, and write compact
    xml_bytes = etree.tostring(tree, encoding="utf-8", xml_declaration=True)
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(xml_bytes, parser)
    etree.ElementTree(root).write(
        str(path),
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=False,
        method="xml"
    )


def find_library_root(target_paths: Iterable[Union[str, Path]], start: Path | None = None) -> Path:
    """
    Walk upward from 'start' (or this file's directory) until one contains any of target_paths.
    """
    start = start or Path(__file__).resolve().parent
    targets = [Path(p) for p in target_paths]
    for folder in (start, *start.parents):
        if any((folder / t).exists() for t in targets):
            return folder
    names = ", ".join(str(t) for t in targets)
    raise RuntimeError(f"Could not locate library root containing any of: {names}")


def _insert_km_for_object(imx_object, km_service: KmService, ribbons: List[str]) -> None:
    """
    Given an IMX object, insert KM comment and location element if it has a Point geometry.
    Collect its kilometer ribbon XML for later insertion.
    """
    geom = getattr(imx_object, 'geometry', None)
    if not isinstance(geom, Point):
        return

    # Fetch KM data
    result = km_service.get_km(geom.x, geom.y)
    loc_elem = etree.fromstring(result.imx_ribbon_locations())

    # Insert comment and location XML
    geo_node = imx_object.element.find(f".//{{{IMSPOOR_NS}}}GeographicLocation")
    if geo_node is not None:
        parent = geo_node.getparent()
        idx = parent.index(geo_node)
        comment = etree.Comment(
            f"KmValue {result.display} added by kmService open-imx.nl, see docs for accuracy disclaimer"
        )
        parent.insert(idx + 1, comment)
        parent.insert(idx + 2, loc_elem)

    # Collect unique ribbons
    ribbon_xml = result.imx_kilometer_ribbons()
    if ribbon_xml not in ribbons:
        ribbons.append(ribbon_xml)


def _collect_km_ribbons(container: ImxContainer, km_service: KmService) -> List[str]:
    """
    Traverse all features in the IMX container and insert KM info where applicable.
    Return the unique kilometer ribbons collected.
    """
    ribbons: List[str] = []
    for obj in container.get_all():
        _insert_km_for_object(obj, km_service, ribbons)
    return ribbons


def _build_ribbons_element(ribbons: list[str]) -> etree._Element:
    """
    Wrap ribbon fragments into a single <KilometerRibbons xmlns:gml="...">…</KilometerRibbons>
    so that the gml: prefix is declared for all children.
    """
    xml = (
        f'<KilometerRibbons xmlns:gml="{GML_NS}">\n'
        + "\n".join(ribbons)
        + "\n</KilometerRibbons>"
    )
    return etree.fromstring(xml)


def _update_signaling_design(root: etree._Element, ribbons_elem: etree._Element) -> None:
    """
    Insert the KilometerRibbons element immediately after the Demarcations node.
    """
    dem = root.find(f".//{{{IMSPOOR_NS}}}Demarcations")
    if dem is None:
        return
    parent = dem.getparent()
    idx = parent.index(dem)
    parent.insert(idx + 1, ribbons_elem)


def add_km_to_imx_xml_file(imx_container_path: str | Path, output_path: str | Path | None) -> None:
    """
    Main entry point: add kilometer markers to an IMX file, validate, and repackage.
    """
    if isinstance(imx_container_path, str):
        imx_path = Path(imx_container_path)
    out_path = Path(output_path) if output_path else Path.cwd()

    # Prepare services and container
    km_service = _get_km_service()
    container = ImxContainer(str(imx_path))

    # Collect and insert KM data
    ribbons = _collect_km_ribbons(container, km_service)
    if not ribbons:
        raise RuntimeError("No kilometer ribbons generated; check object geometries.")
    ribbons_elem = _build_ribbons_element(ribbons)

    # Update signaling design XML tree
    sig_design = container.files.signaling_design
    if not sig_design or sig_design.root is None:
        raise RuntimeError("Signaling design not found in IMX container.")
    _update_signaling_design(sig_design.root, ribbons_elem)

    # Extract, modify, and repackage
    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        with zipfile.ZipFile(imx_path, 'r') as zf:
            zf.extractall(tmpdir)

        # Copy disclaimer markdown
        lib_root = find_library_root(["data", "markdowns", "km-kibbon-values-disclaimer.md"])
        notes = tmpdir / "data-notes"
        notes.mkdir(exist_ok=True)
        shutil.copy(
            lib_root / "data" / "markdowns" / "km-kibbon-values-disclaimer.md",
            notes
        )

        # Write updated XML
        xml_out = tmpdir / sig_design.path.name
        sig_design.root.write(str(xml_out), method='c14n2')

        shutil.copy(
            lib_root / "data" / "markdowns" / "container-xml-formating-disclaimer.md",
            notes
        )

        # Validate against XSD
        xsd_path = lib_root / "data" / "xsd-12.0.0" / "IMSpoor-SignalingDesign.xsd"
        schema = xmlschema.XMLSchema(str(xsd_path))
        errors = list(schema.iter_errors(str(xml_out)))

        # Write validation report
        report = notes / "xsd-validation-report.md"
        with report.open('w') as md:
            md.write("# Schema Details\n\n")
            md.write(f"```text\nSchema: {schema}\n```\n\n")
            md.write("# Validation Errors\n\n| Path | Reason |\n|------|--------|\n")
            for err in errors:
                md.write(f"| `{err.path}` | {err.reason} |\n")




        # Recreate container and rename
        new_container = create_container(str(tmpdir), out_path)
        final_name = f"{imx_path.stem}-add-km{''.join(imx_path.suffixes)}"
        final_path = Path(new_container).parent / final_name
        Path(new_container).rename(final_path)
