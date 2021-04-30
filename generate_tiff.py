import qgis.core
import qgis.gui
import qgis.PyQt.QtCore
import qgis.PyQt.QtGui
import urllib
import owslib.wmts
import argparse
import time
import rasterio
import rasterio.plot
import functions_coordinates
import typing


def main(xmin: float, ymin: float, xmax: float, ymax: float,
    input_epsg: typing.Optional[int] = None, display = False,
    name: typing.Optional[str] = "tile",
    resolution: typing.Optional[float] = 0.2):

    # Convert the coordinates if not in EPSG:3857
    if input_epsg is not None and input_epsg is not 3857:
        xmin, ymin = functions_coordinates.convert_to_IGN(
            xmin, ymin, in_epsg)
        xmax, ymax = functions_coordinates.convert_to_IGN(
            xmax, ymax, in_epsg)

    # Launch a Qgis app
    QGS = qgis.core.QgsApplication([], False)
    QGS.initQgis()

    # Set the extent of the wanted image
    extent = qgis.core.QgsRectangle(xmin, ymin, xmax, ymax)

    # The url for the free and without account access to the IGN WMTS server
    WMTS_URL_GETCAP = "https://wxs.ign.fr/pratique/geoportail/wmts?SERVICE%3D"\
        "WMTS%26REQUEST%3DGetCapabilities"
    WMTS = owslib.wmts.WebMapTileService(WMTS_URL_GETCAP)

    # The name of the satellite image
    LAYER_NAME = "ORTHOIMAGERY.ORTHOPHOTOS"
    WMTS_LAYER = WMTS[LAYER_NAME]
    LAYER_TITLE = WMTS_LAYER.title

    # Set the parameters for the WMTS request
    WMTS_URL_PARAMS = {
        "SERVICE": "WMTS",
        "VERSION": "1.0.0",
        "REQUEST": "GetCapabilities",
        "layers": LAYER_NAME,
        "crs": "EPSG:3857",
        "format": "image/jpeg",
        "styles": "normal",
        "tileMatrixSet": "PM",
        "tileMatrix": "21",
        "url": WMTS_URL_GETCAP
    }

    # Parse these parameters
    WMTS_URL_FINAL = urllib.parse.unquote(urllib.parse.urlencode(WMTS_URL_PARAMS))

    # Check if the layer is still available
    WMTS_LAYER = qgis.core.QgsRasterLayer(WMTS_URL_FINAL, "raster-layer", "wms")
    if WMTS_LAYER.isValid():
        qgis.core.QgsProject.instance().addMapLayer(WMTS_LAYER)
    else:
        print(qgis_wmts_layer_manual.error().message())

    # Change the extent of the layer
    WMTS_LAYER.setExtent(extent)

    # Create the settings for the rederer
    settings = qgis.core.QgsMapSettings()
    settings.setLayers([WMTS_LAYER])
    # Default backgroud is black
    settings.setBackgroundColor(qgis.PyQt.QtGui.QColor(255, 255, 255))
    # The size of the image is the wanted extent divided by the resoltion in meters per pixel
    settings.setOutputSize(qgis.PyQt.QtCore.QSize(extent.width()/resolution, extent.height()/resolution))
    settings.setExtent(WMTS_LAYER.extent())
    
    # Reder the image
    render = qgis.core.QgsMapRendererParallelJob(settings)

    def finished():
        img = render.renderedImage()
        img.save(name + ".tif", "png")

    render.finished.connect(finished)

    render.start()

    loop = qgis.PyQt.QtCore.QEventLoop()
    render.finished.connect(loop.quit)
    loop.exec_()
    
    # Exit the Qgis app
    QGS.exitQgis()

    # Display the result image if needed
    if display:
        img_file = name + '.tif'
        img = rasterio.open(img_file)
        rasterio.plot.show(img)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "xmin",
        help = "latitude or abscissa value of the bottom left corner",
        type = float
    )
    parser.add_argument(
        "ymin",
        help = "longitude or ordinate value of the bottom left corner",
        type = float
    )
    parser.add_argument(
        "xmax",
        help = "latitude or abscissa value of the top right corner",
        type = float
    )
    parser.add_argument(
        "ymax",
        help = "longitude or ordinate value of the top right corner",
        type = float
    )
    parser.add_argument(
        "--epsg",
        help = "use to specify the espg system of the coordinates",
        type = int
    )
    parser.add_argument(
        "--resolution",
        help = "use to specify a resolution in meters per pixel (default 0.2)",
        type = float,
        default = 0.2
    )
    parser.add_argument(
        "--time",
        help = "use to print the execution time",
        action = "store_true"
    )
    parser.add_argument(
        "--display",
        help = "use to display the generated tif file",
        action = "store_true"
    )
    parser.add_argument(
        "--path",
        help = "use to specify the path for the output tif file without the extension .tif",
        type = str,
        default = "tile"
    )
    args = parser.parse_args()

    start = time.time()
    main(args.xmin, args.ymin, args.xmax, args.ymax, args.epsg, args.display, args.path, args.resolution)
    end = time.time()
    duration = end - start
    if args.time:
        print(duration, "secondes")
