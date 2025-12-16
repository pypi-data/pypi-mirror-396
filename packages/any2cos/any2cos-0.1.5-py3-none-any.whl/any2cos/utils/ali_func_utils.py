import alibabacloud_oss_v2 as oss
from rich.progress import Progress, TextColumn, BarColumn, \
    TimeElapsedColumn, TimeRemainingColumn
import os
import pickle
from matplotlib import pyplot as plt

def count_size(FactSize):
    m_strSize = "";
    # FactSize is bit
    if FactSize < 1024.00:
        m_strSize = '{:.2f}'.format(FactSize) + " Byte"
    elif FactSize >= 1024.00 and FactSize < 1048576:
        m_strSize = '{:.2f}'.format(FactSize / 1024.00) + " KB"
    elif FactSize >= 1048576 and FactSize < 1073741824:
        m_strSize = '{:.2f}'.format(FactSize / 1024.00 / 1024.00, 2) + " MB"
    elif FactSize >= 1073741824:
        m_strSize = '{:.2f}'.format(FactSize / 1024.00 / 1024.00 / 1024.00) + " GB"
    return m_strSize

class Handler(object):
    def __init__(self, progress = None):
        self.progress_value = 0
        self.progress = progress
        
    def __call__(self, args):
        def callback_interface(n, complete, total):
            step = int(round(complete * 100 / total)) - self.progress_value
            self.progress.advance(self.upload_tqdm, advance = step)
            self.progress_value = int(round(complete * 100 / total))
        client = oss.Client(args["cfg"])

        if args["mode"] == "down" or args["mode"] == "up":
            self.upload_tqdm = self.progress.add_task(description="传输进度", total = 100)
            object_path_in_oss = os.path.join(args["cos_start_root"], os.path.basename(args["local_fpath"]))
            object_path_in_local = args["local_fpath"]
            if args["mode"] == "down":
                downloader = client.downloader()
                result = downloader.download_file(
                    oss.GetObjectRequest(
                            bucket = args["bucket"],
                            key = object_path_in_oss,
                            progress_fn = callback_interface,
                        ),
                        filepath= object_path_in_local
                )
                print("Downloaded: ", count_size(result.written))
            else:
                uploader = client.uploader()
                result = uploader.upload_file(
                    oss.PutObjectRequest(
                        bucket = args["bucket"],
                        key = object_path_in_oss,
                        progress_fn = callback_interface,
                    ),
                    filepath= object_path_in_local
                )
                if result.status_code == 200:
                    print("Upload Success")
                else:
                    print(result.status_code)

        elif args["mode"] == "ls":
            fnames = []
            paginator = client.list_objects_v2_paginator()
            for page in paginator.iter_page(oss.ListObjectsV2Request(
                    bucket=args["bucket"],
                    prefix=args["cos_start_root"],
                )
            ):
                for o in page.contents:
                    if o.key.replace(args["cos_start_root"], "") != "":
                        print(f'{o.key.replace(args["cos_start_root"], "")}, [Size]: {count_size(o.size)}, [Last]: {str(o.last_modified)[:19]}')
                        fnames.append(o.key)
            return fnames

        elif args["mode"] == "rm":
            result = client.delete_object(oss.DeleteObjectRequest(
                bucket=args["bucket"],
                key = args["cos_start_root"],
            ))
        
        elif args["mode"] == "cls":
            paginator = client.list_objects_v2_paginator()
            for page in paginator.iter_page(oss.ListObjectsV2Request(
                    bucket=args["bucket"],
                    prefix=args["clipboard_start_root"], # 指定前缀为"exampledir/",即只列出"exampledir/"目录下的所有对象
                )
            ):
                for o in page.contents:
                    if o.key.replace(args["clipboard_start_root"], "") != "":       
                        result = client.delete_object(oss.DeleteObjectRequest(
                            bucket=args["bucket"],
                            key = o.key,
                        ))


def cli_handler(action_cfg, any2cos_cfg):
    id = any2cos_cfg["id"]
    token = any2cos_cfg["token"]
    bucket = any2cos_cfg["bucket"]
    region = any2cos_cfg["region"]
    cos_start_root = any2cos_cfg["cos_start_root"]
    endpoint = any2cos_cfg["endpoint"]

    credentials_provider = oss.credentials.StaticCredentialsProvider(id, token)
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider
    cfg.region = region
    cfg.endpoint = endpoint
    
    if action_cfg["mode"] == "ls":
        args = dict(
            cfg = cfg,
            bucket = bucket,
            cos_start_root = cos_start_root,
            mode = "ls",
        )
    elif action_cfg["mode"] == "down":
        args = dict(
            cfg = cfg,
            bucket = bucket,
            cos_start_root = cos_start_root,
            local_fpath = action_cfg["local_fpath"],
            mode = "down",
        )
    elif action_cfg["mode"] == "up":
        args = dict(
            cfg = cfg,
            bucket = bucket,
            cos_start_root = cos_start_root,
            local_fpath = action_cfg["local_fpath"],
            mode = "up",
        )
    else:
        return None

    with Progress(TextColumn("[progress.description]{task.description}"), BarColumn(), \
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), TimeRemainingColumn(),\
                    TimeElapsedColumn()) as progress:
            handler = Handler(progress)
            handler(args)


def matplotlib_handler(action_cfg, any2cos_cfg):
    id = any2cos_cfg["id"]
    token = any2cos_cfg["token"]
    bucket = any2cos_cfg["bucket"]
    region = any2cos_cfg["region"]
    cos_start_root = any2cos_cfg["cos_start_root"]
    endpoint = any2cos_cfg["endpoint"]

    credentials_provider = oss.credentials.StaticCredentialsProvider(id, token)
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider
    cfg.region = region
    cfg.endpoint = endpoint
    
    args = dict(
        cfg = cfg,
        bucket = bucket,
        cos_start_root = cos_start_root,
        local_fpath = action_cfg["win_name"],
        mode = "down",
    )

    with Progress(TextColumn("[progress.description]{task.description}"), BarColumn(), \
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), TimeRemainingColumn(),\
                    TimeElapsedColumn()) as progress:
            handler = Handler(progress)
            handler(args)

    with open(action_cfg["win_name"], "rb") as _f:
        dat_bin = pickle.load(action_cfg["win_name"])
        plt.imshow(dat_bin)
        plt.show()