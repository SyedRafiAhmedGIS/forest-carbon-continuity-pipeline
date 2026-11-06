# 🤝 Handover & Onboarding Path
*Target Time-to-Productivity for New Analyst: < 4 Hours*

This repository is built on the philosophy: **"If I leave tomorrow, what survives me?"** 
The system speaks for itself. No "it works on my machine" excuses.

## 🕒 The Rehearsed Path

### ⏱️ Hour 1: Quickstart (Zero External Setup)
1. Clone the repo and run `conda env create -f environment.yaml` (or `docker compose up`).
2. Open `notebooks/00_Smart_Upload_Preview.ipynb`.
3. Upload the provided sample data (`data/sample_nfi.csv`). See the upload validated end-to-end in < 60 mins — then run notebooks 01–06 (each one executes its engine module on bundled synthetic scenes) and `99_Master_Orchestrator.ipynb` for the full automated run.

### ⏱️ Hour 2: Contracts & Validation
1. Read the stage-contract docs in this folder.
2. Run the test suite: `pytest tests/`.
3. Understand exact I/O guarantees per phase (e.g., CRS is always ETRS89/UTM 29N).

### ⏱️ Day 1: Verification & Replay
1. Re-render last month's production map.
2. Diff against the archive. Confirm byte-level match.
3. *Capstone Rule:* If this path breaks, the handover is broken—not the person.

### ⏱️ Week 1: Prove the System Accepts Change
1. Ship one real configuration change via Pull Request (e.g., swap `threshold_dbh: 10` to `12`).
2. **Automated Guardrails:** Every PR triggers Unit Tests, Integration Tests, and a Golden Image Diff. If any gate fails, the build is rejected automatically.

## 🛡️ Fail-Loud: Bad Data Never Silently Drops
- **Validation Gates:** Per-stage checks enforce CRS consistency, nodata limits, and valid NDVI ranges.
- **Quarantine Protocol:** Failed tiles route immediately to `/quarantine/` with diagnostic JSON logs (Error Code, Timestamp, Tile ID, Input Hash).
- **Deterministic Replay:** Every output GeoTIFF carries embedded tags (`PROVENANCE_COMMIT_SHA`, `INPUT_HASH`). Anyone can query the file to see exactly which code version and source data produced that pixel value.

## ✅ Verification Record
`pytest tests/` (5 gates) and a full synthetic end-to-end replay (reproject → SAR mask → NDVI → Tier-2 carbon → provenance embedding) were executed and passed before handover. Results, environment versions and output checksums are in [`docs/VERIFICATION_LOG.md`](VERIFICATION_LOG.md).
