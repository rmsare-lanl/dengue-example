"""
Convert a CSV with Lat, Lon coordinates to an ESRI Shapefile
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

def csv_to_shapefile(in_filename):
    out_filename = in_filename.replace('.csv', '.shp')
    df = pd.read_csv(in_filename)

    crs = {'init': 'epsg:4326'}
    geometry = [Point(xy) for xy in zip(df.Longitude, df.Latitude)]
    df = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
    df.to_file(driver='ESRI Shapefile', filename=out_filename)
