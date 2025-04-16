from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsProject,
    QgsField,
    QgsFeature,
    QgsVectorLayer,
    QgsGeometry,
    QgsPointXY,
    QgsPalLayerSettings,
    QgsVectorLayerSimpleLabeling,
    QgsTextFormat
)

# Get the active layer and selected features (assuming a 3D linestring layer)
layer = iface.activeLayer()
selected_feats = layer.selectedFeatures()

# Create an in-memory point layer with the same CRS as your active layer
crs = layer.crs().authid()
mem_layer = QgsVectorLayer(f"Point?crs={crs}", "Vertices", "memory")
provider = mem_layer.dataProvider()

# Add a field to store the Z value
provider.addAttributes([QgsField("z_value", QVariant.Double)])
mem_layer.updateFields()

# Iterate over each vertex using the vertices() iterator
for feat in selected_feats:
    geom = feat.geometry()
    for pt in geom.vertices():
        # pt is a QgsPoint, which includes x, y and z values.
        new_feat = QgsFeature()
        # Create a point geometry from x and y (for map placement)
        new_geom = QgsGeometry.fromPointXY(QgsPointXY(pt.x(), pt.y()))
        new_feat.setGeometry(new_geom)
        # Set the attribute to the Z coordinate
        new_feat.setAttributes([pt.z()])
        provider.addFeature(new_feat)

mem_layer.updateExtents()
QgsProject.instance().addMapLayer(mem_layer)

# Set up labeling using QgsVectorLayerSimpleLabeling
label_settings = QgsPalLayerSettings()
label_settings.fieldName = "z_value"
label_settings.enabled = True

# Optionally, set up text formatting
text_format = QgsTextFormat()
text_format.setSize(10)  # Adjust size as needed
label_settings.setFormat(text_format)

labeling = QgsVectorLayerSimpleLabeling(label_settings)
mem_layer.setLabeling(labeling)
mem_layer.setLabelsEnabled(True)
mem_layer.triggerRepaint()