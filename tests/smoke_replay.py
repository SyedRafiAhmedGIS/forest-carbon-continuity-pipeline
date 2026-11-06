"""Handover smoke test: verifies the whole pipeline actually runs, then writes docs/VERIFICATION_LOG.md."""
import hashlib
import json
import os
import platform
import py_compile
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(REPO)
sys.path.insert(0, os.path.join(REPO, "src"))

import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from rasterio.transform import from_bounds  # noqa: E402

RESULTS = []


def check(name, fn):
    try:
        info = fn()
        RESULTS.append((name, "PASS", info or ""))
        print(f"PASS  {name}  {info or ''}")
        return True
    except Exception as exc:
        RESULTS.append((name, "FAIL", f"{type(exc).__name__}: {exc}"))
        print(f"FAIL  {name}  {type(exc).__name__}: {exc}")
        return False


def module_version(name):
    try:
        from importlib.metadata import version
        return version(name)
    except Exception:
        return "n/a"


# ----------------------------------------------------------------- 1. syntax
def syntax_all():
    n = 0
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".ipynb_checkpoints")]
        for f in files:
            if f.endswith(".py"):
                py_compile.compile(os.path.join(root, f), doraise=True)
                n += 1
    return f"{n} .py files compile clean"


# ----------------------------------------------------------------- 2. notebooks
def notebooks_valid():
    import nbformat
    n = 0
    nb_dir = os.path.join(REPO, "notebooks")
    for f in sorted(os.listdir(nb_dir)):
        if f.endswith(".ipynb"):
            nb = nbformat.read(os.path.join(nb_dir, f), as_version=4)
            nbformat.validate(nb)
            n += 1
    return f"{n} notebooks pass nbformat validation"


# ----------------------------------------------------------------- 3. synthetic inputs
IN, OUT = "data/input", "data/output"
os.makedirs(IN, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

rng = np.random.default_rng(42)
tr = from_bounds(-6.4, 52.95, -6.1, 53.15, 200, 200)


def write_wgs84(path, arr, dtype):
    with rasterio.open(path, "w", driver="GTiff", height=200, width=200, count=1,
                       dtype=dtype, crs="EPSG:4326", transform=tr) as dst:
        dst.write(arr.astype(dtype), 1)


write_wgs84(f"{IN}/demo_wgs84.tif", rng.random((200, 200)) * 0.8 + 0.1, "float32")
write_wgs84(f"{IN}/demo_s1_vh.tif", 0.02 + rng.random((200, 200)) * 0.06, "float32")
write_wgs84(f"{IN}/demo_s1_vv.tif", 0.08 + rng.random((200, 200)) * 0.15, "float32")
write_wgs84(f"{IN}/demo_s2_nir.tif", rng.random((200, 200)) * 4000 + 1000, "uint16")
write_wgs84(f"{IN}/demo_s2_red.tif", rng.random((200, 200)) * 2500 + 200, "uint16")
sp_profile = {"driver": "GTiff", "height": 200, "width": 200, "count": 1, "dtype": "uint8",
              "crs": "EPSG:25829",
              "transform": from_bounds(598000, 5862000, 604000, 5868000, 200, 200)}
species = rng.choice([1, 2, 3], size=(200, 200), p=[0.5, 0.3, 0.2]).astype("uint8")
with rasterio.open(f"{OUT}/species_map.tif", "w", **sp_profile) as dst:
    dst.write(species, 1)


# ----------------------------------------------------------------- 4. engine steps
def step_reproject():
    from crs_handler import reproject_to_utm29n
    out = reproject_to_utm29n(f"{IN}/demo_wgs84.tif", f"{OUT}/01_reprojected.tif")
    with rasterio.open(out) as ds:
        assert ds.crs.to_epsg() == 25829
    return "EPSG:25829 confirmed"


def step_mask():
    from sar_optical_fusion import apply_cloud_masking
    out = apply_cloud_masking(f"{IN}/demo_s1_vh.tif", f"{IN}/demo_s1_vv.tif", f"{OUT}/02_forest_mask.tif")
    with rasterio.open(out) as ds:
        arr = ds.read(1)
        assert ds.dtypes[0] == "uint8", f"mask dtype {ds.dtypes[0]} != uint8"
    forest = int(arr.sum())
    assert 0 < forest < 40000
    return f"uint8 mask, {forest}/40000 forest pixels"


def step_ndvi():
    from sar_optical_fusion import extract_ndvi_max
    out = extract_ndvi_max(f"{IN}/demo_s2_nir.tif", f"{IN}/demo_s2_red.tif", f"{OUT}/03_ndvi.tif")
    with rasterio.open(out) as ds:
        arr = ds.read(1)
        assert -1.0 <= float(arr.min()) and float(arr.max()) <= 1.0
    return f"range [{arr.min():.3f}, {arr.max():.3f}]"


def step_biomass():
    from carbon_accounting import calculate_tier2_biomass
    out = calculate_tier2_biomass(f"{OUT}/species_map.tif", f"{OUT}/04_carbon_stock.tif")
    with rasterio.open(out) as ds:
        assert ds.count == 2
        bio, unc = ds.read(1), ds.read(2)
    means = {sp: round(float(bio[species == sp].mean()), 1) for sp in (1, 2, 3)}
    cis = {sp: round(float(unc[species == sp].mean()), 1) for sp in (1, 2, 3)}
    return f"2 bands | t/ha per class {means} | CI {cis}"


def step_provenance():
    from metadata_embedder import compute_input_hash, embed_provenance
    src_file = f"{OUT}/04_carbon_stock.tif"
    out = embed_provenance(src_file, f"{OUT}/05_carbon_final_provenance.tif", compute_input_hash(src_file))
    tags = rasterio.open(out).tags()
    expected_sha = hashlib.sha256(open(src_file, "rb").read()).hexdigest()
    assert tags.get("INPUT_HASH") == expected_sha, "INPUT_HASH mismatch"
    assert tags.get("PIPELINE_VERSION") == "1.0.0"
    return f"INPUT_HASH sha256 verified | COMMIT_SHA={tags.get('PROVENANCE_COMMIT_SHA', '')[:8]}"


def step_quarantine():
    from quarantine import log_quarantine
    path = log_quarantine("TILE-SMOKE", "SYNTHETIC_GATE_TEST", "deadbeef", {"msg": "fail-loud drill"})
    report = json.loads(open(path).read())
    assert report["error_code"] == "SYNTHETIC_GATE_TEST" and "timestamp" in report
    return f"{path} (drill, auto-cleaned)"


def step_nfi():
    from nfi_integration import calculate_tree_height, process_nfi_ground_truth
    out = process_nfi_ground_truth("data/sample_nfi.csv", f"{OUT}/nfi_ground_truth.gpkg")
    import geopandas as gpd
    gdf = gpd.read_file(out)
    assert len(gdf) == 9, f"expected 9 plots after DBH gate, got {len(gdf)}"
    row = gdf[gdf["plot_id"] == "IE-001"].iloc[0]
    expected = 11.2 * np.tan(np.radians(28.5)) + 1.3
    assert abs(float(row["Height"]) - expected) < 1e-9
    assert str(gdf.crs) == "EPSG:25829"
    h1 = round(float(calculate_tree_height(11.2, np.radians(28.5), 1.3)), 2)
    return f"10 plots -> 9 after DBH gate | IE-001 H={h1} m | CRS EPSG:25829"


def step_pytest():
    proc = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"],
                          capture_output=True, text=True, cwd=REPO)
    last = [l for l in proc.stdout.strip().splitlines() if l.strip()][-1] if proc.stdout else proc.stderr[-200:]
    if proc.returncode != 0:
        raise AssertionError(last)
    return last


def step_gif():
    from PIL import Image
    p = "docs/pipeline_demo.gif"
    im = Image.open(p)
    frames = getattr(im, "n_frames", 1)
    assert frames == 5, f"expected 5 frames, got {frames}"
    return f"{frames} frames, {im.size[0]}x{im.size[1]} px, {os.path.getsize(p):,} bytes"


def step_handover_gif():
    from PIL import Image
    p = "docs/handover_continuity_demo.gif"
    im = Image.open(p)
    frames = getattr(im, "n_frames", 1)
    assert frames == 5, f"expected 5 frames, got {frames}"
    return f"{frames} frames, {im.size[0]}x{im.size[1]} px, {os.path.getsize(p):,} bytes"


def step_polish():
    checks = {
        "LICENSE": lambda c: c.startswith("MIT License") and "Syed Rafi Ahmed" in c,
        "CONTRIBUTING.md": lambda c: "Week 1" in c and "Pull Request" in c,
        "Makefile": lambda c: any(l.startswith("\t") for l in c.splitlines()) and "pytest tests/" in c,
        ".github/workflows/ci.yml": lambda c: "pytest tests/" in c and "actions/checkout" in c,
        ".env.example": lambda c: "COPERNICUS_USERNAME" in c,
    }
    for path, rule in checks.items():
        with open(os.path.join(REPO, path), encoding="utf-8") as fh:
            content = fh.read()
        assert rule(content), f"guardrail failed for {path}"
    return " | ".join(checks.keys())


def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO).decode().strip()
    except Exception:
        return "unknown (git repo not initialised)"


check("1. Python syntax (all modules)", syntax_all)
check("2. Notebook validity (nbformat)", notebooks_valid)
check("3. Engine: CRS reprojection", step_reproject)
check("4. Engine: SAR cloud-proof mask", step_mask)
check("5. Engine: NDVI composite", step_ndvi)
check("6. Engine: Tier-2 carbon + 95% CI", step_biomass)
check("7. Engine: provenance embedding", step_provenance)
check("8. Fail-loud quarantine drill", step_quarantine)
check("9. NFI ground-truth ingest", step_nfi)
check("10. pytest gate suite", step_pytest)
check("11. Pipeline GIF (5 frames)", step_gif)
check("12. Handover & Continuity GIF (5 frames)", step_handover_gif)
check("13. Professional polish (LICENSE | CONTRIBUTING | Makefile | CI | .env.example)", step_polish)

# ----------------------------------------------------------------- log
os.makedirs("quarantine", exist_ok=True)
commit = git_commit()
fails = [r for r in RESULTS if r[1] != "PASS"]
drill = "quarantine/fail_TILE-SMOKE.json"
if os.path.exists(drill):
    os.remove(drill)

lines = [
    "# ✅ Verification Log — Pre-Handover Audit",
    "",
    "*Auto-generated by the handover smoke test on 2026-11-06. Regenerate anytime with `python tests/smoke_replay.py`.*",
    "",
    "## Environment",
    "| Component | Version |",
    "| --- | --- |",
    f"| Python | {platform.python_version()} |",
    f"| rasterio | {module_version('rasterio')} |",
    f"| numpy | {module_version('numpy')} |",
    f"| geopandas | {module_version('geopandas')} |",
    f"| pytest | {module_version('pytest')} |",
    f"| Git commit at run | `{commit[:12]}` |",
    "",
    "## Gate Results",
    "| # | Gate | Result | Evidence |",
    "| --- | --- | --- | --- |",
]
for i, (name, status, info) in enumerate(RESULTS, 1):
    mark = "✅" if status == "PASS" else "❌"
    lines.append(f"| {i} | {name} | {mark} {status} | {info} |")

lines += [
    "",
    "## End-to-End Replay Outputs (`data/output/`)",
]
for fname in sorted(os.listdir(OUT)):
    size = os.path.getsize(os.path.join(OUT, fname))
    lines.append(f"- `{fname}` — {size:,} bytes")

lines += [
    "",
    "## Notes",
    "- Synthetic scenes are seeded (`numpy default_rng(42)`), so the replay is deterministic.",
    "- Notebook 04 executes a U-Net forward/backward pass; PyTorch is required at runtime and was validated structurally in the verification sandbox (torch not installed there).",
    "- `data/input/`, `data/output/` and `quarantine/` are runtime folders (git-ignored); notebooks regenerate their contents.",
    "",
]
with open("docs/VERIFICATION_LOG.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print()
print(f"SUMMARY: {sum(1 for r in RESULTS if r[1] == 'PASS')}/{len(RESULTS)} gates passed")
sys.exit(1 if fails else 0)
