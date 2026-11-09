# Real Sentinel Data — Quickstart (Wicklow Pilot)

This guide replaces the demo stubs with real Copernicus data. The pipeline
talks to the **Copernicus Data Space Ecosystem (CDSE)** — the official
successor of the retired SciHub — through **openEO**, its cloud-processing
API. Everything is processed server-side; you only download small result
files (GeoTIFF).

Pilot AOI: **Wicklow Mountains** (same window as `configs/ireland_config.yaml`).

---

## 1. Create the (free) account

1. Open <https://dataspace.copernicus.eu> and click **Register** (top right).
2. Confirm your e-mail address and log in once in the browser.
3. No tokens or secrets to manage — the Python client uses OAuth device flow.

## 2. Install the openEO Python client

```bash
pip install "openeo>=0.30"
```

## 3. Connect and authenticate

```python
import openeo

conn = openeo.connect("https://openeo.dataspace.copernicus.eu")
conn.authenticate_oidc()   # prints a URL + device code
```

A browser window opens (or copy the printed URL), you log in with your CDSE
account and approve the request. The token is cached under
`~/.config/openeo/` — you authenticate once per machine, not per script.

## 4. Define the AOI

Wicklow bounding box (WGS84). Put the same values under `aoi:` in
`configs/ireland_config.yaml`:

```python
bbox = {"west": -6.45, "south": 52.98,
        "east": -6.10, "north": 53.18, "crs": "EPSG:4326"}
```

## 5. Sentinel-2 NDVI with cloud masking

`SENTINEL2_L2A` already contains the scene-classification band `SCL`.
Mask everything that is not clean land: SCL **3** = cloud shadow,
**8** = cloud medium probability, **9** = cloud high probability,
**10** = thin cirrus.

```python
s2 = conn.load_collection(
    "SENTINEL2_L2A",
    spatial_extent=bbox,
    temporal_extent=["2024-06-01", "2024-08-31"],
    bands=["B04", "B08", "SCL"],
    max_cloud_cover=80,
)

scl = s2.band("SCL")
cloud = (scl == 3) | (scl == 8) | (scl == 9) | (scl == 10)
s2 = s2.filter_bands(["B04", "B08"]).mask(cloud)

ndvi = s2.ndvi(red="B04", nir="B08")
monthly = ndvi.aggregate_temporal_period("month", reducer="mean")

job = monthly.execute_batch("data/raw/wicklow_ndvi_2024_summer.tif",
                            outformat="GTiff", title="wicklow-ndvi")
```

`execute_batch` returns immediately. Poll with `job.status()` or watch the
**Jobs** tab at openeo.dataspace.copernicus.eu. A county-size AOI over one
summer finishes in a few minutes on the free tier.

## 6. Sentinel-1 SAR composite

GRD backscatter arrives as **linear power**. Convert to dB yourself — the
classic mistake is skipping the conversion or using 20·log₁₀:

```python
s1 = conn.load_collection(
    "SENTINEL1_GRD",
    spatial_extent=bbox,
    temporal_extent=["2024-06-01", "2024-08-31"],
    bands=["VV", "VH"],
)
s1 = s1.aggregate_temporal_period("month", reducer="mean")
job = s1.execute_batch("data/raw/wicklow_s1_2024_summer.tif",
                       outformat="GTiff", title="wicklow-s1")
```

Then locally, e.g. in `01_Preprocessing_CRS.ipynb`:

```python
import numpy as np
sigma0 = raster.read(1)        # linear power, always positive
db = 10 * np.log10(sigma0)     # power -> dB (not 20*log10)
```

## 7. Wire it into the repo

| Step | Where | What to do |
|---|---|---|
| 1 | `configs/ireland_config.yaml` | paste the `aoi:` bbox and the 2024 summer dates |
| 2 | `data/raw/` | keep the two GeoTIFFs from steps 5–6 (create the folder if missing) |
| 3 | notebooks `01` – `06` | Run All — reprojection to **EPSG:2157** (Irish Transverse Mercator) happens in notebook 01 |
| 4 | `notebooks/99_Master_Orchestrator.ipynb` | end-to-end run |
| 5 | tests | `pytest tests/ -v` |

## 8. Ground-truth labels (two options)

- **Official — National Forest Inventory (NFI):** plot data are distributed by
  the Department of Agriculture, Food and the Marine (DAFM) on request
  (gov.ie — search "National Forest Inventory"). Free for research, licence
  required. Apply early: approval takes a few weeks.
- **Open proxy — Copernicus HRL Dominant Leaf Type:** 10 m raster with
  broadleaved / coniferous / mixed classes, direct download from
  <https://land.copernicus.eu> (High Resolution Layers). Good enough to demo
  `03_NFI_Ground_Truth.ipynb` and `04_ML_Species_Classification.ipynb`.

## 9. Sanity ranges (Ireland, summer)

| Layer | Healthy range | Red flag |
|---|---|---|
| NDVI (S2, Jun–Aug) | 0.60 – 0.92 over forest | > 1 or < 0 everywhere → scaling bug |
| VV dB (S1) | −20 … −8 | ≈ 0 dB → you skipped 10·log₁₀ |
| VH dB (S1) | −28 … −15 | — |
| Working CRS | EPSG:2157 (ITM) | degrees from EPSG:4326 leaking into area maths |

## 10. Batch jobs for bigger AOIs

For an all-Ireland run switch the AOI to
`{"west": -10.7, "south": 51.4, "east": -5.9, "north": 55.45,
"crs": "EPSG:4326"}` and keep using `execute_batch` — never `.download()`,
which runs synchronously and times out above ~100 km².

## Troubleshooting

| Symptom | Cause → fix |
|---|---|
| `authenticate_oidc()` hangs | device code expired (valid < 10 min) → re-run and approve faster |
| 402 / quota errors | free-tier fair-use limit → shrink the AOI or shorten the window |
| `memory-limit` job failure | too many bands × time steps → reduce to monthly means first or set 20 m resolution |
| NDVI all zeros | SCL mask too aggressive → inspect class values with `np.unique(scl)` |
| GeoTIFF opens grey in QGIS | missing overviews → `gdaladdo file.tif` |

## Before you publish

```bash
pip install nbstripout
nbstripout notebooks/*.ipynb      # strip notebook outputs before commit
```

Archive the `v1.0` tag on Zenodo for a DOI, and cite your data sources:
Copernicus Sentinel-1/2 (ESA), HRL Dominant Leaf Type (Copernicus Land
Monitoring Service), National Forest Inventory (DAFM).
