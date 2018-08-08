"""
Data analysis of water and Dengue occurrence data
"""

import os
import pyproj
import pandas as pd
import geopandas as gpd
import statsmodels.api as sm
from functools import partial
from matplotlib import pyplot as plt
from shapely import ops


def main():
    
    df1 = gpd.read_file('data/Antonioetal_PLOSOne_2017_S1.shp')
    df2 = gpd.read_file('data/test.shp')
    
    df = gpd.sjoin(df2, df1, 'inner')
    df = normalize_dengue(df)
    df = normalize_water(df)

    plot_data(df, 2002)
    plt.show()


def normalize_dengue(df):
    dengue_columns = [col for col in df.columns 
                          if 'den' in col 
                          and 'norm' not in col]
    for dengue_col in dengue_columns:
        pop_col = dengue_col.replace('den', 'pop')
        ratio_col = dengue_col.replace('den', 'den_norm')
        df[ratio_col] = df[dengue_col] / df[pop_col]
    return df


def normalize_water(df):
    conversion_factor = (30 * 30)  # m2 in pixel
    water_columns = [col for col in df.columns
                         if 'water' in col
                         and 'norm' not in col]
    for water_col in water_columns:
        df[water_col] = df[water_col].astype(float)
        ratio_col = water_col.replace('water', 'water_norm')
        for i, row in df.iterrows():
            projected = project_wgs84(row.geometry)
            area = projected.area / conversion_factor
            df[ratio_col] = df[water_col] / area
    return df


def plot_data(df, year): 
    dengue_col = 'den_{}'.format(year)
    pop_col = 'pop_{}'.format(year)
    water_col = 'water_{}'.format(year)

    fig, ax = plt.subplots(1, 3, figsize=(12, 4))
    df.plot(dengue_col, cmap='Reds', ax=ax[0])
    df.plot(pop_col, ax=ax[1])
    df.plot(water_col, cmap='Blues', ax=ax[2])
    plt.suptitle('Raw')

    dengue_col = 'den_norm_{}'.format(year)
    df[dengue_col] *= 1000.
    water_col = 'water_norm_{}'.format(year)

    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    df.plot(dengue_col, cmap='Reds', ax=ax[0])
    df.plot(water_col, cmap='Blues', ax=ax[1])
    plt.suptitle('Normalized')


def project_wgs84(geometry):
    geometry_proj = ops.transform(
                        partial(pyproj.transform, 
                            pyproj.Proj(init='EPSG:4326'), 
                            pyproj.Proj(proj='aea', 
                                lat1=geometry.bounds[1], 
                                lat2=geometry.bounds[3])), 
                        geometry)
    return geometry_proj


if __name__ == "__main__":
    main()
