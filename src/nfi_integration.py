import numpy as np
import pandas as pd


def calculate_tree_height(distance_m, angle_rad, observer_height_m):
    """H = D * tan(theta) + h  (laser hypsometer / relascope geometry)."""
    return distance_m * np.tan(angle_rad) + observer_height_m


def process_nfi_ground_truth(nfi_path, output_path,
                             target_crs="EPSG:25829", dbh_threshold_cm=10.0):
    """
    Ingest NFI ground truth (CSV/XLSX with x, y columns, or any GDAL-readable
    vector), apply the DBH >= threshold gate, compute tree heights, and write
    a GeoPackage in the region's target CRS (see configs/*.yaml).
    """
    import geopandas as gpd  # lazy: heavy geo stack only needed here

    if nfi_path.endswith('.csv') or nfi_path.endswith('.xlsx'):
        df = pd.read_csv(nfi_path) if nfi_path.endswith('.csv') else pd.read_excel(nfi_path)
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y), crs="EPSG:4326")
    else:
        gdf = gpd.read_file(nfi_path)
    if 'DBH' in gdf.columns:
        gdf = gdf[gdf['DBH'] >= dbh_threshold_cm]
    if all(c in gdf.columns for c in ['Distance', 'Angle', 'ObsHeight']):
        gdf['Height'] = calculate_tree_height(gdf['Distance'], np.radians(gdf['Angle']), gdf['ObsHeight'])
    gdf = gdf.to_crs(target_crs)
    gdf.to_file(output_path, driver="GPKG")
    return output_path
