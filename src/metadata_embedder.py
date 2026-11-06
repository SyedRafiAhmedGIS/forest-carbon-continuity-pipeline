import hashlib
import subprocess

import rasterio


def get_git_hash():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except Exception:
        return "unknown"


def compute_input_hash(path):
    """SHA-256 of the raw file bytes -> the INPUT_HASH for the audit trail."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def embed_provenance(input_path, output_path, input_hash=None):
    """
    Deterministic Replay: embeds the Git commit SHA and input data hash
    into the GeoTIFF *tags* for an immutable audit trail.

    Note: extra keys passed through `meta.update()` are dropped by rasterio
    as unknown driver creation options, so dataset tags are the only
    storage that actually persists.
    """
    git_sha = get_git_hash()
    if input_hash is None:
        input_hash = compute_input_hash(input_path)

    with rasterio.open(input_path) as src:
        meta = src.meta.copy()
        data = src.read()

    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(data)
        dst.update_tags(
            PROVENANCE_COMMIT_SHA=git_sha,
            INPUT_HASH=input_hash,
            PIPELINE_VERSION='1.0.0',
        )

    print(f"✅ Embedded Provenance: SHA={git_sha[:8]}, InputHash={input_hash[:8]}")
    return output_path
