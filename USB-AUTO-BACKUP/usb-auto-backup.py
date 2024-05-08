#!/usr/bin/env python3
import sys
import os
import datetime
import subprocess

############################# LOGGING BLOCK #############################
import sys
import logging

logging.basicConfig(filename='/var/log/usb_copy.log', level=logging.INFO)
logging.info(f'Script triggered with device: {sys.argv[1]}')
############################# LOGGING BLOCK #############################

# Constants
SIZE_LIMIT = 1.0  # 1.0 TiB
BASE_PATH = "/home/CONTAINER"  # Base path for backups
EJECT_AFTER_COMPLETION = False  # Control flag for ejecting the USB device after copying

# Retrieve the total device size and return the size in TiB (float)
def get_device_size(device_path):
    size_bytes = int(subprocess.check_output(['blockdev', '--getsize64', device_path]))
    return size_bytes / (1024 ** 4)  # convert bytes to TiB

# Check if device specified in the command-line argument is already mounted
def check_mount(device_path, mount_point):
    if not os.path.ismount(mount_point):
        os.makedirs(mount_point, exist_ok=True)
        subprocess.run(['mount', device_path, mount_point], check=True)

def main(device):
    device_path = f"/dev/{device}1"
    mount_point = f"/mnt/{device}"

    # Check mount status and mount if necessary
    check_mount(device_path, mount_point)

    # Get device size and check against SIZE_LIMIT (units = TiB)
    dev_size = get_device_size(device_path)
    if dev_size > SIZE_LIMIT:
        print(f"{device_path} has {dev_size:.2f} TiB, which is above the limit of {SIZE_LIMIT:.1f} TiB.")

        if EJECT_AFTER_COMPLETION:
            subprocess.run(['umount', mount_point])  # Unmount the device if it exceeds the size limit
        return

    # Prepare target folders
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    target_folder = os.path.join(BASE_PATH, date_str)
    finished_folder = os.path.join(BASE_PATH, f"FINISHED-{date_str}")
    os.makedirs(target_folder, exist_ok=True)

    # Copy files
    print("Copying files...")
    subprocess.run(['./rsync-copy-handler.sh', mount_point, target_folder])

    # If EJECT_AFTER_COMPLETION is true, then unmount and eject the device
    if EJECT_AFTER_COMPLETION:
        subprocess.run(['umount', device_path])
        subprocess.run(['eject', mount_point])

    # Recursively change owner to the core group and rename after all is done
    subprocess.run(['chown','-R',':core',target_folder])
    os.rename(target_folder, finished_folder)

    # Print completion message
    if EJECT_AFTER_COMPLETION:
        print(f"Finished copying and ejected {device}.")
    else:
        print(f"Finished copying and did not eject {device}.")

# Detect if argument was passed and run the script; print usage if no arguments
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 script.py <device_name>")
    else:
        main(sys.argv[1])
