from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFields,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes,
)

# Define the CRS as EPSG:7415 (Amersfoort / RD New + NAP height)
crs_code = "EPSG:7415"


def create_memory_layer(geom_type, layer_name):
    """
    Create a memory layer for a given geometry type with the common fields.
    The layer uses the EPSG:7415 coordinate system.
    """
    if geom_type == QgsWkbTypes.PointGeometry:
        geom_str = "Point"
    elif geom_type == QgsWkbTypes.LineGeometry:
        geom_str = "LineString"
    elif geom_type == QgsWkbTypes.PolygonGeometry:
        geom_str = "Polygon"
    else:
        return None

    # Set up the URI for the memory layer with the specified CRS.
    uri = f"{geom_str}?crs={crs_code}"
    mem_layer = QgsVectorLayer(uri, layer_name, "memory")
    provider = mem_layer.dataProvider()

    # Define common attribute fields.
    fields = QgsFields()
    fields.append(QgsField("@puic", QVariant.String))
    fields.append(QgsField("path", QVariant.String))

    provider.addAttributes(fields)
    mem_layer.updateFields()
    return mem_layer


# Create aggregated memory layers for each geometry type.
aggregated_points = create_memory_layer(QgsWkbTypes.PointGeometry, "Aggregated Points")
aggregated_lines = create_memory_layer(QgsWkbTypes.LineGeometry, "Aggregated Lines")
aggregated_polygons = create_memory_layer(QgsWkbTypes.PolygonGeometry, "Aggregated Polygons")


def ensure_additional_fields(target_layer, source_feature):
    """
    For the given source feature, add (if needed) the 'name' field and any field
    whose name starts with 'RailConnectionInfo' to the target layer.
    """
    source_fields = source_feature.fields()
    target_fields = target_layer.fields()

    # Loop through all field names in the source feature.
    for field in source_fields:
        fname = field.name()
        if fname == "name" or fname.startswith("RailConnectionInfo"):
            if target_fields.indexFromName(fname) == -1:
                # Field does not exist in target; add it.
                new_field = QgsField(fname, field.type())
                target_layer.dataProvider().addAttributes([new_field])
                target_layer.updateFields()
                # Update our local copy of target fields.
                target_fields = target_layer.fields()


def process_group(group, point_layer, line_layer, polygon_layer):
    """
    Recursively process the group layer tree and add features from each vector layer
    into the appropriate aggregated memory layer.
    """
    for child in group.children():
        if isinstance(child, QgsLayerTreeGroup):
            process_group(child, point_layer, line_layer, polygon_layer)
        elif isinstance(child, QgsLayerTreeLayer):
            layer = child.layer()
            # Process only vector layers.
            if not isinstance(layer, QgsVectorLayer):
                continue

            # Determine the target aggregated layer based on geometry type.
            geom_type = layer.geometryType()
            if geom_type == QgsWkbTypes.PointGeometry:
                target_layer = point_layer
            elif geom_type == QgsWkbTypes.LineGeometry:
                target_layer = line_layer
            elif geom_type == QgsWkbTypes.PolygonGeometry:
                target_layer = polygon_layer
            else:
                continue  # Skip unsupported geometries

            features_to_add = []
            for feat in layer.getFeatures():
                # Ensure the target layer contains additional desired fields.
                ensure_additional_fields(target_layer, feat)

                # Create a new feature using the updated target layer fields.
                new_feat = QgsFeature(target_layer.fields())
                new_feat.setGeometry(feat.geometry())
                # Copy the common attributes.
                new_feat.setAttribute("@puic", feat.attribute("@puic"))
                new_feat.setAttribute("path", feat.attribute("path"))
                # Copy additional attributes if present.
                if feat.fields().indexFromName("name") != -1:
                    new_feat.setAttribute("name", feat.attribute("name"))
                # Iterate over all fields from the source feature.
                for fname in feat.fields().names():
                    if fname.startswith("RailConnectionInfo"):
                        new_feat.setAttribute(fname, feat.attribute(fname))
                features_to_add.append(new_feat)

            if features_to_add:
                target_layer.dataProvider().addFeatures(features_to_add)
                target_layer.updateExtents()


def aggregate_group_layers(group_name="t2-geojson"):
    """
    Locate the specified group and process its children recursively.
    Then add the aggregated layers to the current QGIS project.
    """
    root = QgsProject.instance().layerTreeRoot()
    group = root.findGroup(group_name)
    if group is None:
        print(f"Group '{group_name}' not found.")
        return

    process_group(group, aggregated_points, aggregated_lines, aggregated_polygons)

    # Add the new aggregated layers to the project.
    QgsProject.instance().addMapLayer(aggregated_points)
    QgsProject.instance().addMapLayer(aggregated_lines)
    QgsProject.instance().addMapLayer(aggregated_polygons)
    print("Aggregation complete.")


# Run the aggregation using the default group "t2-geojson".
aggregate_group_layers()
