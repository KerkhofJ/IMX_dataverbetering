def add_meest_recent_layer():
    # Define the base URL for the WMS service
    base_url = "https://luchtfoto.prorail.nl/erdas-iws/ogc/wms/Luchtfoto?"

    # Define the WMS parameters including the desired layer 'meest_recent'
    params = {
        "service": "WMS",
        "version": "1.3.0",
        "request": "GetMap",
        "layers": "meest_recent",
        "styles": "",
        "format": "image/png",
        "crs": "EPSG:28992",  # You may adjust the CRS as needed
    }

    # Construct the URL string with the parameters
    url_params = "&".join([f"{key}={value}" for key, value in params.items()])
    url_with_params = f"url={base_url}{url_params}"

    # Create the WMS layer using QgsRasterLayer. The third parameter 'wms' tells QGIS to use the WMS provider.
    layer = QgsRasterLayer(url_with_params, "Luchtfoto Meest Recent", "wms")

    # Check if the layer is valid
    if not layer.isValid():
        QgsMessageLog.logMessage("Failed to load 'meest_recent' WMS layer", level=Qgis.Critical)
        return None

    # Add the layer to the current project instance
    QgsProject.instance().addMapLayer(layer)
    return layer
