import numpy as np
import rasterio

def calculate_tier2_biomass(species_map_path, output_path):
    with rasterio.open(species_map_path) as src:
        species = src.read(1)
        meta = src.meta.copy()
    matrix = {1: 450, 2: 380, 3: 300}
    uncertainty_factors = {1: 0.15, 2: 0.18, 3: 0.25}
    biomass = np.zeros_like(species, dtype=np.float32)
    uncertainty = np.zeros_like(species, dtype=np.float32)
    for sp_id, peak in matrix.items():
        mask = species == sp_id
        biomass[mask] = peak * 0.8
        uncertainty[mask] = biomass[mask] * uncertainty_factors[sp_id] * 1.96
    meta.update(dtype='float32', count=2)
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(biomass, 1)
        dst.write(uncertainty, 2)
    return output_path
