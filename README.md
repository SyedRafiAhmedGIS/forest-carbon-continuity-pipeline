# 🌲 Forest Carbon Continuity Pipeline
**A Sentinel-1/2 Hybrid Approach for EU LULUCF Compliance — One Engine. Multiple Climates.**  
*Built for cloud-proof, species-specific, and reproducible carbon accounting.*

![Pipeline Workflow](docs/pipeline_demo.gif)
![Handover & Continuity Philosophy](docs/handover_continuity_demo.gif)

## 🤝 Handover & Onboarding Philosophy
*"If I leave tomorrow, what survives me?"*  
This repository is designed for **< 4 Hour Time-to-Productivity** for any new analyst. No "it works on my machine" excuses.
- **Self-Documenting:** Numbered scripts make execution order obvious.
- **Containerized:** Docker + Conda locks dependencies globally (zero version drift).
- **Fail-Loud:** Bad data never silently drops; it routes to `/quarantine/` with structured JSON diagnostics.
- **Deterministic Replay:** Every output GeoTIFF embeds the `PROVENANCE_COMMIT_SHA` and `INPUT_HASH` for an immutable audit trail.
- **Verified:** `pytest` gate suite + end-to-end synthetic replay executed before handover — see `docs/VERIFICATION_LOG.md`.

## 🚀 Quick Start (Hour 1)
1. **Setup:** `conda env create -f environment.yaml` (or `docker compose up`)
2. **Activate:** `conda activate forest-carbon-continuity`
3. **Run:** Open `notebooks/00_Smart_Upload_Preview.ipynb`, upload the bundled sample `data/sample_nfi.csv`, and see the data validated end-to-end.

## Interactive Notebooks - Open in Colab

| # | Phase | Notebook | Open in Colab |
|---|-------|----------|:---:|
| 00 | Smart Upload & Preview | [`00_Smart_Upload_Preview.ipynb`](https://github.com/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/00_Smart_Upload_Preview.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/00_Smart_Upload_Preview.ipynb) |
| 01 | Preprocessing & CRS | [`01_Preprocessing_CRS.ipynb`](https://github.com/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/01_Preprocessing_CRS.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/01_Preprocessing_CRS.ipynb) |
| 02 | Cloud Masking & S1/S2 Fusion | [`02_Cloud_Masking_Fusion.ipynb`](https://github.com/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/02_Cloud_Masking_Fusion.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/02_Cloud_Masking_Fusion.ipynb) |
| 03 | NFI Ground Truth | [`03_NFI_Ground_Truth.ipynb`](https://github.com/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/03_NFI_Ground_Truth.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/03_NFI_Ground_Truth.ipynb) |
| 04 | ML Species Classification | [`04_ML_Species_Classification.ipynb`](https://github.com/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/04_ML_Species_Classification.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/04_ML_Species_Classification.ipynb) |
| 05 | Carbon Stock & Uncertainty | [`05_Carbon_Stock_Uncertainty.ipynb`](https://github.com/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/05_Carbon_Stock_Uncertainty.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/05_Carbon_Stock_Uncertainty.ipynb) |
| 06 | Forest Density & Land-Cover Layers | [`06_Forest_Density_LandCover_Layers.ipynb`](https://github.com/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/06_Forest_Density_LandCover_Layers.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/06_Forest_Density_LandCover_Layers.ipynb) |
| 99 | Master Orchestrator (all phases) | [`99_Master_Orchestrator.ipynb`](https://github.com/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/99_Master_Orchestrator.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SyedRafiAhmedGIS/forest-carbon-continuity-pipeline/blob/main/notebooks/99_Master_Orchestrator.ipynb) |

## 🏗️ Architecture
- **`src/`**: Core modular Python logic (The Engine)
- **`notebooks/`**: Interactive Colab Wrappers with Smart Uploads & Previews
- **`configs/`**: Region-specific YAML (Ireland, UK, Scandinavia)
- **`data/`**: Bundled sample NFI plot data (`sample_nfi.csv`) + runtime inputs/outputs
- **`tests/`**: Automated guardrails (imports, CRS contract, provenance, quarantine)
- **`docs/`**: "Code as Documentation", Verification Log & Detailed Onboarding Path

## 📊 Pipeline Phases
1. **CRS Reprojection:** WGS84 $\rightarrow$ ETRS89/UTM 29N (EPSG:25829)
2. **Cloud-Proof Masking:** Sentinel-1 VH/VV radar fusion.
3. **NFI Integration:** Relascope/Laser Hypsometer math ($H = D \times \tan(\theta) + h$).
4. **ML Classification:** U-Net (Dice+BCE Loss) for Sitka Spruce, Lodgepole Pine, Native Mixed.
5. **Carbon Accounting:** Species $\times$ Age Matrix with $\pm 95\%$ CI uncertainty.
6. **Density & LULC Layers:** VDF, MDF, Open Forest, Nurseries, Barren Land mapping.

---
*Built by Syed Rafi Ahmed | M.Tech Remote Sensing & GIS*  
*Contact: alsyedrafiahmed@gmail.com*
