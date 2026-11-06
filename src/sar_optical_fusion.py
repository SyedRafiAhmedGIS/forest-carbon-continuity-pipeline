import numpy as np
import rasterio


def apply_cloud_masking(sar_vh_path, sar_vv_path, output_mask_path):
    """
    Cloud-proof forest mask from Sentinel-1 VH/VV radar fusion.
    Writes a uint8 mask regardless of the source dtype (Sentinel-1 GRD
    arrives as uint16; writing a uint8 array against that profile fails).
    """
    with rasterio.open(sar_vh_path) as vh, rasterio.open(sar_vv_path) as vv:
        vh_linear, vv_linear = vh.read(1).astype(float), vv.read(1).astype(float)
        vh_db = 10 * np.log10(np.where(vh_linear > 0, vh_linear, 1e-10))
        ratio = np.divide(vh_linear, vv_linear, out=np.zeros_like(vh_linear), where=vv_linear != 0)
        forest_mask = (vh_db > -15) & (ratio > 0.15)
        mask = np.where(forest_mask, 1, 0).astype(np.uint8)
        meta = vh.meta.copy()
        meta.update({"dtype": "uint8", "count": 1, "nodata": None})
        with rasterio.open(output_mask_path, 'w', **meta) as dst:
            dst.write(mask, 1)
    return output_mask_path


def extract_ndvi_max(nir_path, red_path, output_ndvi_path):
    """
    NDVI max composite from Sentinel-2 NIR/Red.
    Writes float64 regardless of the source dtype (reflectance arrives
    scaled as uint16; the float NDVI array cannot share that profile).
    """
    with rasterio.open(nir_path) as nir, rasterio.open(red_path) as red:
        nir_data, red_data = nir.read(1).astype(float), red.read(1).astype(float)
        ndvi = np.divide(
            (nir_data - red_data), (nir_data + red_data),
            out=np.zeros_like(nir_data), where=(nir_data + red_data) != 0,
        )
        meta = nir.meta.copy()
        meta.update({"dtype": "float64", "count": 1, "nodata": None})
        with rasterio.open(output_ndvi_path, 'w', **meta) as dst:
            dst.write(ndvi, 1)
    return output_ndvi_path
