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


def main(xmin, ymin, xmax, ymax, input_epsg : typing.Optional[int] = None,
    geodetic=False, display=False, name : typing.Optional[str] = None):

    if name is None:
        name = "tile"

    in_epsg = input_epsg if input_epsg is not None else 3857

    xmin, ymin = functions_coordinates.convert_to_IGN(
        xmin, ymin, in_epsg)
    xmax, ymax = functions_coordinates.convert_to_IGN(
        xmax, ymax, in_epsg)

    QGS = qgis.core.QgsApplication([], False)
    QGS.initQgis()

    extent = qgis.core.QgsRectangle(xmin, ymin, xmax, ymax)

    WMTS_URL_GETCAP = "https://wxs.ign.fr/pratique/geoportail/wmts?SERVICE%3D"\
        "WMTS%26REQUEST%3DGetCapabilities"
    WMTS = owslib.wmts.WebMapTileService(WMTS_URL_GETCAP)
    LAYER_NAME = "ORTHOIMAGERY.ORTHOPHOTOS"
    WMTS_LAYER = WMTS[LAYER_NAME]
    LAYER_TITLE = WMTS_LAYER.title

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
        "url": WMTS_URL_GETCAP,
        "dpiMode": "8"
    }

    WMTS_URL_FINAL = urllib.parse.unquote(urllib.parse.urlencode(WMTS_URL_PARAMS))

    WMTS_LAYER = qgis.core.QgsRasterLayer(WMTS_URL_FINAL, "raster-layer", "wms")
    if WMTS_LAYER.isValid():
        qgis.core.QgsProject.instance().addMapLayer(WMTS_LAYER)
    else:
        print(qgis_wmts_layer_manual.error().message())

    layer = qgis.core.QgsProject.instance().mapLayersByName("raster-layer")[0]

    layer.setExtent(extent)

    settings = qgis.core.QgsMapSettings()
    settings.setLayers([layer])
    settings.setBackgroundColor(qgis.PyQt.QtGui.QColor(255, 255, 255))
    settings.setOutputSize(qgis.PyQt.QtCore.QSize(extent.width()*5, extent.height()*5))
    settings.setExtent(layer.extent())
    settings.setOutputDpi(8)
    
    render = qgis.core.QgsMapRendererParallelJob(settings)

    def finished():
        img = render.renderedImage()
        img.save(name + ".tif", "png")

    render.finished.connect(finished)

    render.start()

    loop = qgis.PyQt.QtCore.QEventLoop()
    render.finished.connect(loop.quit)
    loop.exec_()
    
    QGS.exitQgis()

    if display:
        img_file = name + '.tif'
        img = rasterio.open(img_file)
        rasterio.plot.show(img)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "xmin",
        help="latitude or abscissa value of the bottom left corner",
        type=float
    )
    parser.add_argument(
        "ymin",
        help="longitude or ordinate value of the bottom left corner",
        type=float
    )
    parser.add_argument(
        "xmax",
        help="latitude or abscissa value of the top right corner",
        type=float
    )
    parser.add_argument(
        "ymax",
        help="longitude or ordinate value of the top right corner",
        type=float
    )
    parser.add_argument(
        "--epsg",
        help="use to specify the espg system of the coordinates",
        type=int
    )
    parser.add_argument(
        "--geodetic",
        help="use if the coordinates are in geodetic projection",
        action="store_true"
    )
    parser.add_argument(
        "--time",
        help="use to print the execution time",
        action="store_true"
    )
    parser.add_argument(
        "--display",
        help="use to display the generated tif file",
        action="store_true"
    )
    parser.add_argument(
        "--path",
        help="use to specify the path for the output tif file without the extension .tif",
        type=str
    )
    args = parser.parse_args()

    start = time.time()
    main(args.xmin, args.ymin, args.xmax, args.ymax, args.epsg, args.geodetic, args.display, args.path)
    end = time.time()
    duration = end - start
    if args.time:
        print(duration, "secondes")
