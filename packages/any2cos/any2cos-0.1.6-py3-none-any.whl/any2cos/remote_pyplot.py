from any2cos.utils.ali_func_utils import Handler
import os
import pickle
from matplotlib import pyplot as plt
from .api import upload, download

def imshow(dat, win_name = "demo", cache_root = '__rmplt__'):
    os.makedirs(cache_root, exist_ok=True)
    save_fpath = os.path.join(cache_root, win_name)
    with open(save_fpath, 'wb') as f:
        pickle.dump(dat, f)
    upload(save_fpath)
    print(f"To show in local GUI: `anycos -i <win_name>` or `any2cos --imshow <win_name>`;\n And press any key with `ENTER` to continue process...\nNow <win_name> is `{win_name}`")
    input()

def show(win_name = "demo", cache_root = '__rmplt__'):
    os.makedirs(cache_root, exist_ok=True)
    save_fpath = os.path.join(cache_root, win_name)
    download(save_fpath)
    with open(save_fpath, "rb") as f:
        dat = pickle.load(f)
    plt.imshow(dat)
    plt.show()
