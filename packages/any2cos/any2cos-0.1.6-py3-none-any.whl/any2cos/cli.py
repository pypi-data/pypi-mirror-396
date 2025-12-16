import time
import shutil
import sys
import os
import logging
import argparse
import platform
import json
from any2cos.utils.cfg_manner import write_cfg
from any2cos.utils.ali_func_utils import cli_handler, matplotlib_handler
from any2cos.remote_pyplot import show

cfg_in_platform = dict(
    dawrwin = "",
    linux = os.path.expanduser("~") + "/.config/any2cos",
    windows = "C://.config/any2cos"
)

cfg_root = cfg_in_platform[platform.system().lower()]
os.makedirs(cfg_root, exist_ok=True)

if os.path.exists(os.path.join(cfg_root, "any2cos.json")):
    with open(os.path.join(cfg_root, "any2cos.json"), "r") as f:
        any2cos_cfg = json.load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ls",
        "-l",
        "-L",
        help="List your cos files in root",
        action = "store_true",
    )
    parser.add_argument(
        "--down",
        "-d",
        "-D",
        help="Download file from cos",
        default = None,
        type = str,
        required=False
    )
    parser.add_argument(
        "--up",
        "-u",
        "-U",
        help="Upload local file to cos",
        default = None,
        type = str,
        required=False
    )
    parser.add_argument(
        "--imshow",
        "-i",
        "-I",
        help="imshow matplotlib window",
        default = None,
        type = str,
        required=False
    )

    subparsers = parser.add_subparsers(dest='command', help='Custom commands')
    set_parser = subparsers.add_parser('set', help='Settings writer')
    set_parser.add_argument('set_key', help='第一个参数，如 id')
    set_parser.add_argument('set_value', help='第二个参数，如值')

    args = parser.parse_args()
    
    if args.ls == True:
        cli_handler(action_cfg=dict(mode = "ls"), any2cos_cfg = any2cos_cfg)
    elif args.up is not None:
        cli_handler(action_cfg=dict(mode = "up", local_fpath = args.up), any2cos_cfg=any2cos_cfg)
    elif args.down is not None:
        cli_handler(action_cfg=dict(mode = "down", local_fpath = args.down), any2cos_cfg=any2cos_cfg)
    elif args.imshow is not None:
        show(args.imshow)
    elif args.command == 'set':
        write_cfg(cfg_root, args.set_key, args.set_value)
    else:
        print("No this command, -h to see usage details.")

if __name__ == "__main__":
    main()
