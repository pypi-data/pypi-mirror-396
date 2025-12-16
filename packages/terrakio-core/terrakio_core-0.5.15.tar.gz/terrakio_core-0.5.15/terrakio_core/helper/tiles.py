import geopandas as gpd
import shapely.geometry

def escape_newline(string):
    if isinstance(string, list):
        return [s.replace('\\n', '\n') for s in string]
    else:
        return string.replace('\\n', '\n')


def get_bounds(aoi_file, crs, to_crs):
    aoi : gpd.GeoDataFrame = gpd.read_file(aoi_file)
    aoi = aoi.set_crs(crs, allow_override=True)
    if to_crs != crs:
        aoi = aoi.to_crs(to_crs)
    bounds = aoi.geometry[0].bounds
    return *bounds, aoi


def tile_generator(x_min, y_min, x_max, y_max, aoi, crs, res, tile_size, expression, output, mask):
    i_max = int((x_max-x_min)/(tile_size*res)) + 1
    j_max = int((y_max-y_min)/(tile_size*res)) + 1
    for j in range(0, int(j_max)):
        for i in range(0, int(i_max)):
            x = x_min + i*(tile_size*res)
            y = y_max - j*(tile_size*res)
            geom = shapely.geometry.box(x, y-(tile_size*res), x + (tile_size*res), y)
            if not aoi.geometry[0].intersects(geom):
                continue
            if mask:
                geom = geom.intersection(aoi.geometry[0])
                if geom.is_empty:
                    continue
            feat  = {"type": "Feature", "geometry": geom.__geo_interface__}
            data = {
                "feature": feat,
                "in_crs": crs,
                "out_crs": crs,
                "resolution": res,
                "expr" : expression,
                "output" : output,
            }
            yield data, i , j


def tiles(
    name: str,
    aoi : str, 
    expression: str = "red=S2v2#(year,median).red@(year =2024) \n red",
    output: str = "netcdf",
    tile_size : float = 1024,
    crs : str = "epsg:3577",
    to_crs: str = None,
    res: float = 10,
    mask: bool = True,
): 
    reqs = []
    if to_crs is None:
        to_crs = crs
    x_min, y_min, x_max, y_max, aoi = get_bounds(aoi, crs, to_crs)
    for tile_req, i, j in tile_generator(x_min, y_min, x_max, y_max, aoi, to_crs, res, tile_size, expression, output, mask):
        req_name = f"{name}_{i:02d}_{j:02d}"
        reqs.append({"group": "tiles", "file": req_name, "request": tile_req})

    groups = list(set(dic["group"] for dic in reqs))

    return reqs, groups