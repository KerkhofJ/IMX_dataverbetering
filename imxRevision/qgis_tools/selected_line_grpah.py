import matplotlib.pyplot as plt
from qgis.core import QgsProject

# Get the selected feature
layer = iface.activeLayer()  # Assuming the active layer is the one you're working with
selected_features = layer.selectedFeatures()

# Check if any feature is selected
if not selected_features:
    print("No feature selected")
else:
    feature = selected_features[0]  # Assuming you're working with the first selected feature
    geometry = feature.geometry()

    if geometry.isEmpty():
        print("Selected feature has no geometry")
    else:
        # Get the vertices of the geometry
        vertices = geometry.vertices()

        # Create lists to store lengths and Z-values
        lengths = []
        z_values = []

        total_length = 0  # Keep track of the cumulative length along the geometry
        previous_point = None

        for point in vertices:
            # If this is not the first point, calculate the distance from the previous point
            if previous_point is not None:
                distance = previous_point.distance(point)
                total_length += distance

            # Store the Z value and the cumulative length
            lengths.append(total_length)
            z_values.append(point.z())

            previous_point = point  # Set the previous point for the next iteration

        # Plot the graph of Z-values along the length
        plt.figure(figsize=(10, 6))
        plt.plot(lengths, z_values, marker='o', linestyle='-', color='b')
        plt.title("Z-values Along the Length of the Geometry")
        plt.xlabel("Length (meters)")
        plt.ylabel("Z-value")
        plt.grid(True)
        plt.show()

