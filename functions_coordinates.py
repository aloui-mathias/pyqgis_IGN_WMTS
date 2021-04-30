import pyproj

def convert_coord(x : float, y : float, input_epsg : int,
    output_epsg : int):

    input_crs = pyproj.CRS.from_epsg(input_epsg)
    output_crs = pyproj.CRS.from_epsg(output_epsg)

    input_is_geodetic = (input_crs == input_crs.geodetic_crs)
    output_is_geodetic = (output_crs == output_crs.geodetic_crs)

    diff_geodetic = (input_is_geodetic != output_is_geodetic)

    proj = pyproj.Transformer.from_crs(input_crs, output_crs)

    if diff_geodetic and input_is_geodetic:
        coord = proj.transform(y, x)
    else:
        coord = proj.transform(x, y)    
    
    if diff_geodetic and output_is_geodetic:
        return coord[1], coord[0]
    else:
        return coord[0], coord[1]

def convert_to_IGN(x : float, y : float,
    input_epsg : int):

    return convert_coord(x, y, input_epsg, 3857)

def convert_from_IGN(x : float, y : float,
    output_epsg : int):

    return convert_coord(x, y, 3857, output_epsg)



