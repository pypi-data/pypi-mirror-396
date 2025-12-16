from typing import Dict

def require_keys(cfg: Dict, keys):
    missing = [k for k in keys if k not in cfg]
    if missing:
        raise KeyError(f"Missing required keys: {missing}")
    return True