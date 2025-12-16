import os
import platform
import json
from any2cos.utils.ali_func_utils import cli_handler

cfg_in_platform = dict(
    dawrwin = "",
    linux = "~/.config/any2cos",
    windows = "C://.config/any2cos"
)

cfg_root = cfg_in_platform[platform.system().lower()]
os.makedirs(cfg_root, exist_ok=True)

if os.path.exists(os.path.join(cfg_root, "any2cos.json")):
    with open(os.path.join(cfg_root, "any2cos.json"), "r") as f:
        any2cos_cfg = json.load(f)

def upload(local_file_path):
    cli_handler(action_cfg=dict(mode = "up", local_fpath = local_file_path), 
                any2cos_cfg=any2cos_cfg)

def download(target_local_file_path):
    cli_handler(action_cfg=dict(mode = "down", local_fpath = target_local_file_path), 
                any2cos_cfg=any2cos_cfg)