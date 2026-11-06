import json
import os
import sys

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_bounds

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


# ---------------------------------------------------------------
# Gate 1: every core engine module imports cleanly (no heavyweight deps)
# ---------------------------------------------------------------
def test_imports():
    from carbon_accounting import calculate_tier2_biomass
    from crs_handler import reproject_to_utm29n
    from metadata_embedder import embed_provenance
    from nfi_integration import calculate_tree_height
    from quarantine import log_quarantine
    from sar_optical_fusion import apply_cloud_masking, extract_ndvi_max
    assert all(callable(f) for f in (calculate_tier2_biomass, reproject_to_utm29n,
                                     embed_provenance, calculate_tree_height,
                                     log_quarantine, apply_cloud_masking,
                                     extract_ndvi_max))


# ---------------------------------------------------------------
# Gate 1b: ML stack (U-Net + Dice-BCE) — requires torch
# ---------------------------------------------------------------
def test_ml_modules_constructible():
    pytest.importorskip("torch", reason="PyTorch not installed in this environment")
    import torch
    from ml_models import DiceBCELoss, UNetSpeciesClassifier
    model = UNetSpeciesClassifier(in_ch=6, out_ch=3)
    loss_fn = DiceBCELoss()
    x = torch.randn(1, 6, 32, 32)
    y = torch.randint(0, 2, (1, 3, 32, 32)).float()
    loss = loss_fn(model(x), y)
    loss.backward()
    assert loss.item() > 0


# ---------------------------------------------------------------
# Gate 2: hypsometer math H = D * tan(theta) + h
# ---------------------------------------------------------------
def test_tree_height_math():
    from nfi_integration import calculate_tree_height
    expected = 11.2 * np.tan(np.radians(28.5)) + 1.3
    assert calculate_tree_height(11.2, np.radians(28.5), 1.3) == pytest.approx(expected)


# ---------------------------------------------------------------
# Gate 3: Fail-Loud quarantine writes structured JSON
# ---------------------------------------------------------------
def test_quarantine_writes_structured_log(tmp_path, monkeypatch):
    import quarantine
    monkeypatch.chdir(tmp_path)
    path = quarantine.log_quarantine("TILE-TEST", "E_TEST", "deadbeef", {"detail": "smoke"})
    report = json.loads(open(path).read())
    assert report["tile_id"] == "TILE-TEST"
    assert report["error_code"] == "E_TEST"
    assert report["input_hash"] == "deadbeef"
    assert "timestamp" in report


# ---------------------------------------------------------------
# Gate 4: CRS contract — WGS84 in, ETRS89/UTM 29N out
# ---------------------------------------------------------------
def test_crs_reprojection_contract(tmp_path):
    from crs_handler import reproject_to_utm29n
    src_path = str(tmp_path / "wgs84.tif")
    out_path = str(tmp_path / "utm.tif")
    profile = {"driver": "GTiff", "height": 50, "width": 50, "count": 1,
               "dtype": "float32", "crs": "EPSG:4326",
               "transform": from_bounds(-6.4, 52.95, -6.1, 53.15, 50, 50)}
    with rasterio.open(src_path, 'w', **profile) as dst:
        dst.write(np.full((50, 50), 0.5, dtype='float32'), 1)
    reproject_to_utm29n(src_path, out_path)
    with rasterio.open(out_path) as dst:
        assert dst.crs.to_epsg() == 25829


# ---------------------------------------------------------------
# Gate 5: provenance tags really persist in the output GeoTIFF
# ---------------------------------------------------------------
def test_provenance_tags_persist(tmp_path):
    from metadata_embedder import embed_provenance
    src_path = str(tmp_path / "in.tif")
    out_path = str(tmp_path / "out.tif")
    profile = {"driver": "GTiff", "height": 10, "width": 10, "count": 1,
               "dtype": "uint8", "crs": "EPSG:25829",
               "transform": from_bounds(598000, 5862000, 600000, 5864000, 10, 10)}
    with rasterio.open(src_path, 'w', **profile) as dst:
        dst.write(np.arange(100, dtype='uint8').reshape(10, 10), 1)
    embed_provenance(src_path, out_path, input_hash="a" * 64)
    tags = rasterio.open(out_path).tags()
    assert tags.get("PROVENANCE_COMMIT_SHA")
    assert tags.get("INPUT_HASH") == "a" * 64
    assert tags.get("PIPELINE_VERSION") == "1.0.0"
