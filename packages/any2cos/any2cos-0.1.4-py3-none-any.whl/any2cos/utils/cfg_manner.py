import os
import json

def write_cfg(cfg_root, cfg_key, cfg_value):
    if os.path.exists(os.path.join(cfg_root, "any2cos.json")):
        with open(os.path.join(cfg_root, "any2cos.json"), "r") as f:
            any2cos_cfg = json.load(f)
    else:
        any2cos_cfg = dict()

    any2cos_cfg[cfg_key] = cfg_value

    with open(os.path.join(cfg_root, "any2cos.json"), 'w') as f:
        json.dump(any2cos_cfg, f)