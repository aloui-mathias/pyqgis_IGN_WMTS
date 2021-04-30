import pyproj

# Convert coordinates from one EPSG to another
def convert_coord(x: float, y: float,
                  input_epsg: int,
                  output_epsg: int) -> float, float:

    # Create the input and output crs
    input_crs = pyproj.CRS.from_epsg(input_epsg)
    output_crs = pyproj.CRS.from_epsg(output_epsg)

    # Create the transformer
    proj = pyproj.Transformer.from_crs(input_crs, output_crs)

    # If the input coordinates are geodetic but the ouput is not:
    # Inverse the input coordinates
    if input_crs.is_geographic and not output_crs.is_geographic:
        coord = proj.transform(y, x)
    else:
        coord = proj.transform(x, y)    
    
    # If the output coordinates are geodetic but the input is not:
    # Inverse the output coordinates
    if output_crs.is_geographic and not input_crs.is_geographic:
        return coord[1], coord[0]
    else:
        return coord[0], coord[1]


def convert_to_IGN(x: float, y: float, input_epsg: int) -> float, float:
    return convert_coord(x, y, input_epsg, 3857)

def convert_from_IGN(x: float, y: float, output_epsg: int) -> float, float:
    return convert_coord(x, y, 3857, output_epsg)
