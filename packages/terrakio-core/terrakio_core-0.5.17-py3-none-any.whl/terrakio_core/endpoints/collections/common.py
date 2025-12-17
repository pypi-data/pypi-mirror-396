import enum
import json
import dateutil.parser
import geopandas as gpd
import shapely.geometry
import typer
from typing import Any

class OutputTypes(enum.Enum):
    geotiff = 'geotiff'
    png = 'png'
    netcdf = 'netcdf'
    json = 'json'
    json_v2 = 'json_v2'
    csv = 'csv'

class Region(str, enum.Enum):
    aus = "aus"
    eu = "eu"
    us = "us"

regions = {
    Region.aus : {
        "name" : "australia-southeast1", 
        "url" : "https://terrakio-server-candidate-573248941006.australia-southeast1.run.app", 
        "bucket" : "terrakio-mass-requests"
    },
    
    Region.eu : {
        "name" : "europe-west4", 
        "url" : "https://terrakio-server-candidate-573248941006.europe-west4.run.app", 
        "bucket" : "terrakio-mass-requests-eu"
    },
    
    Region.us : {
        "name" : "us-central1", 
        "url" : "https://terrakio-server-candidate-573248941006.us-central1.run.app", 
        "bucket" : "terrakio-mass-requests-us"
    },

}

class Dataset_Dtype(enum.Enum):
    uint8 = 'uint8'
    float32 = 'float32'

def tile_generator(x_min, y_min, x_max, y_max, aoi, crs, res, tile_size, expression, output, fully_cover=True):
    i_max = int((x_max-x_min)/(tile_size*res))
    j_max = int((y_max-y_min)/(tile_size*res))
    if fully_cover:
        i_max += 1
        j_max += 1
    for j in range(0, int(j_max)):
        for i in range(0, int(i_max)):
            x = x_min + i*(tile_size*res)
            y = y_max - j*(tile_size*res)
            bbox = shapely.geometry.box(x, y-(tile_size*res), x + (tile_size*res), y)
            if not aoi.geometry[0].intersects(bbox):
                continue
            feat  = {"type": "Feature", "geometry": bbox.__geo_interface__}
            data = {
                "feature": feat,
                "in_crs": crs,
                "out_crs": crs,
                "resolution": res,
                "expr" : expression,
                "output" : output.value,
            }
            yield data, i , j


def get_bounds(aoi, crs, to_crs = None):
    gdf : gpd.GeoDataFrame = gpd.read_file(aoi)
    gdf = gdf.set_crs(crs, allow_override=True)
    if to_crs:
        gdf = gdf.to_crs(to_crs)
    bounds = gdf.geometry[0].bounds
    return *bounds, gdf

def validate_date(date: str) -> str:
    try:
        date = dateutil.parser.parse(date)
        return date
    except ValueError:
        print(f"Invalid date: {date}")
        raise typer.BadParameter(f"Invalid date: {date}")

def make_json_serializable(obj):
    """Convert non-JSON-serializable types to JSON-serializable equivalents."""
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    elif hasattr(obj, 'isoformat'):  # Timestamp, datetime, date, time
        return obj.isoformat()
    elif hasattr(obj, 'item'):  # numpy types
        return obj.item()
    else:
        return obj

