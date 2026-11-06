import json
import os
from datetime import datetime, timezone

def log_quarantine(tile_id, error_code, input_hash, details):
    """
    Fail-Loud Protocol: Logs failed tiles with structured diagnostics 
    instead of silently dropping them, enabling automated triage.
    """
    quarantine_dir = "quarantine"
    os.makedirs(quarantine_dir, exist_ok=True)
    
    report = {
        "tile_id": tile_id,
        "error_code": error_code,
        "input_hash": input_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details
    }
    
    filepath = os.path.join(quarantine_dir, f"fail_{tile_id}.json")
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"⚠️ QUARANTINE: Tile {tile_id} failed with {error_code}. Logged to {filepath}")
    return filepath
