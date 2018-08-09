"""
Data analysis of water and Dengue occurrence data
"""

import os
import pyproj
import numpy as np
import pandas as pd
import geopandas as gpd
import statsmodels.api as sm
from functools import partial
from matplotlib import pyplot as plt
from shapely import ops


def main():
    pop_thresh = 1e6

    df1 = gpd.read_file('data/Antonioetal_PLOSOne_2017_S1.shp')
    df2 = gpd.read_file('data/test.shp')
    
    gdf = gpd.sjoin(df2, df1, 'inner')
    gdf = normalize_dengue(gdf)
    gdf = normalize_water(gdf)
    
    """
    years = np.arange(2002, 2013)
    for year in years:
        print('Plotting map of {}'.format(year))
        plot_data(gdf, year)
    """

    names = gdf[gdf.pop_2012 >= pop_thresh].NOME
    print(names)
    for name in names:
        print('Plotting timeseries of {}'.format(name))
        df = to_dataframe(gdf, name)
        plot_timeseries(df, name)


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
    df.plot(dengue_col, cmap='Reds', ax=ax[0], legend=True)
    df.plot(pop_col, ax=ax[1], legend=True)
    df.plot(water_col, cmap='Blues', ax=ax[2], legend=True)
    plt.suptitle('Raw')

    for axis in ax:
        axis.set_xticklabels([])
        axis.set_yticklabels([])

    plt.savefig('fig/raw_{}'.format(year), dpi=300, bbox_inches='tight')

    df[dengue_col] = np.log10(df[dengue_col].values)
    df[pop_col] = np.log10(df[pop_col].values)
    df[water_col] = np.log10(df[water_col].values)

    fig, ax = plt.subplots(1, 3, figsize=(12, 4))
    df.plot(dengue_col, cmap='Reds', ax=ax[0], legend=True)
    df.plot(pop_col, ax=ax[1], legend=True)
    df.plot(water_col, cmap='Blues', ax=ax[2], legend=True)
    plt.suptitle('Log')

    for axis in ax:
        axis.set_xticklabels([])
        axis.set_yticklabels([])

    plt.savefig('fig/log_{}'.format(year), dpi=300, bbox_inches='tight')

    dengue_col = 'den_norm_{}'.format(year)
    df[dengue_col] *= 1000.
    water_col = 'water_norm_{}'.format(year)
    df[water_col] *= 10.

    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    df.plot(dengue_col, cmap='Reds', ax=ax[0], legend=True)
    df.plot(water_col, cmap='Blues', ax=ax[1], legend=True)
    plt.suptitle('Normalized')
    
    df[dengue_col] /= 1000

    for axis in ax:
        axis.set_xticklabels([])
        axis.set_yticklabels([])
    
    plt.savefig('fig/norm_{}'.format(year), dpi=300, bbox_inches='tight')

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    x = np.array(df[water_col].values).astype(float)
    y = np.array(df[dengue_col].values).astype(float)
    ax.plot(x, y, 'ks', markersize=5)
    ax.set_xlabel('Seasonal water area [%]')
    ax.set_ylabel('Dengue cases per 1000 people')
    
    plt.savefig('fig/scatter_{}'.format(year), dpi=300, bbox_inches='tight')
    plt.close('all')


def plot_timeseries(df, city_name):
    fig, ax = plt.subplots(2, 1, sharex=True, figsize=(4, 8))
    ax[0].plot(df.index, df.den_norm, 's-')
    ax[1].plot(df.index, df.water_norm, '^-')
    ax[0].set_ylabel('Dengue cases per 1000 people')
    ax[1].set_ylabel('Seasonal water area [%]')
    
    r = df.corr().values[1,2]
    plt.title(city_name + ' $\rho=${:0.2f}'.format(r))

    plt.savefig('fig/timeseries_{}'.format(city_name), dpi=300, bbox_inches='tight')
    plt.close('all')


def to_dataframe(gdf, name):
    row = gdf[gdf.NOME == name]
    years = [int(col.split('_')[-1]) for col in row.columns
            if 'water' in col
            and 'norm' not in col]
    data = [[y, 
            row.iloc[0]['den_{}'.format(y)], 
            row.iloc[0]['water_{}'.format(y)]] for y in years] 
    
    df = pd.DataFrame(data=data)
    df.columns = ['year', 'den_norm', 'water_norm']

    return df


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
