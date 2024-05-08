#!/usr/bin/env python3
import sys
import os
import shutil
import datetime
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Constants
SIZE_LIMIT = 1.0 * (1024 ** 4)  # 1.0 TiB in bytes
BASE_PATH = "/path/to/backup"  # Base path for backups
THREADS = 5  # Number of concurrent threads for copying

def copy_contents(src, dst):
    # Recursively copy files from src to dst using multiple threads
    if os.path.isdir(src):
        os.makedirs(dst, exist_ok=True)
        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            futures = []
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    futures.append(executor.submit(copy_contents, s, d))
                else:
                    futures.append(executor.submit(shutil.copy2, s, d))
            for future in futures:
                future.result()
    else:
        shutil.copy2(src, dst)

def main(device):
    device_path = f"/dev/{device}"
    mount_point = f"/mnt/{device}"

    # Mount the device
    os.makedirs(mount_point, exist_ok=True)
    os.system(f"mount {device_path} {mount_point}")

    # Determine device size to check against SIZE_LIMIT
    total_size = os.path.getsize(mount_point)
    if total_size > SIZE_LIMIT:
        print(f"Device size ({total_size}) exceeds the limit ({SIZE_LIMIT}).")
        return

    # Prepare target folders
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    target_folder = os.path.join(BASE_PATH, date_str)
    finished_folder = os.path.join(BASE_PATH, f"FINISHED-{date_str}")
    os.makedirs(target_folder, exist_ok=True)

    # Copy files
    print("Copying files...")
    copy_contents(mount_point, target_folder)

    # Unmount and eject the device
    os.system(f"umount {mount_point}")
    os.system(f"eject {device_path}")

    # Rename folder upon completion
    os.rename(target_folder, finished_folder)
    print("Copy complete and device ejected.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 script.py <device_name>")
    else:
        main(sys.argv[1])