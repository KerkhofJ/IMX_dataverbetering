import matplotlib.pyplot as plt
from qgis.core import QgsGeometry

# Get the active layer and selected features
layer = iface.activeLayer()
selected_features = layer.selectedFeatures()

if not selected_features:
    print("No feature selected")
else:
    # Merge all selected geometries
    merged_geometry = QgsGeometry()

    for feature in selected_features:
        if merged_geometry.isEmpty():
            merged_geometry = feature.geometry()
        else:
            merged_geometry = merged_geometry.combine(feature.geometry())

    # Check if merging resulted in a MultiLineString
    if merged_geometry.type() != 1:  # 1 = LineString, 2 = Polygon, 0 = Point
        print("Selected features cannot be merged into a single LineString")
    else:
        # Get vertices of the merged LineString
        vertices = merged_geometry.vertices()

        lengths = []
        z_values = []
        total_length = 0
        previous_point = None

        for point in vertices:
            if previous_point is not None:
                total_length += previous_point.distance(point)

            lengths.append(total_length)
            z_values.append(point.z())
            previous_point = point

        # Plot the graph
        plt.figure(figsize=(10, 6))
        plt.plot(lengths, z_values, marker='o', linestyle='-', color='b')
        plt.title("Z-values Along the Length of the Merged Geometry")
        plt.xlabel("Length (meters)")
        plt.ylabel("Z-value")
        plt.grid(True)
        plt.show()











