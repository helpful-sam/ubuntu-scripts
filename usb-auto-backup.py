'''
left off while fixing:

Traceback (most recent call last):
  File "/home/sam/programming/scripts/usb-auto-backup.py", line 23, in <module>
    size_bytes = int(subprocess.check_output(["lsblk", "-b", "-n", "-o", "SIZE", device]).strip())
ValueError: invalid literal for int() with base 10: b'512074186752\n512040632320'

'''

import os
import sys
import subprocess
from datetime import datetime # for generating timestamps on backup folders

# Base path for where to save the copied files
base_path = "/base/path"

# Check if copying only from sde is toggled on
only_sde = True  # Change this to True if you want to only operate on /dev/sde

if only_sde:
    device = "/dev/sde"
    print("Only copying from /dev/sde.")
    if not os.path.exists(device):
        print(f"{device} does not exist. Exiting.")
        sys.exit(0)
else:
    # Device identifier
    device = f"/dev/{sys.argv[1]}"

# Get the size of the device in bytes and convert to TiB (Tebibytes)
size_bytes = int(subprocess.check_output(["lsblk", "-b", "-n", "-o", "SIZE", device]).strip())
size_tib = size_bytes / (1024 ** 4)

# Size limit (1 TiB)
size_limit = 1.0

if size_tib < size_limit:
    # Mount point for the USB
    mount_point = f"/mnt/{os.path.basename(device)}"

    # Check if already mounted
    if subprocess.run(['mountpoint', '-q', mount_point]).returncode == 0:
        print(f"{device} is already mounted.")
    else:
        # Create mount point directory
        os.makedirs(mount_point, exist_ok=True)
        # Mount the device
        subprocess.run(["mount", device, mount_point])

    # Destination directory for the backup, modify it as needed
    current_date = datetime.now().strftime("%Y-%m-%d")
    dest_dir = os.path.join(base_path, device, "-", current_date)

    # Create the destination directory
    os.makedirs(dest_dir, exist_ok=True)

    # Copy the contents of the USB to the destination directory
    subprocess.run(["rsync", "-av", "--progress", f"{mount_point}/", dest_dir])

    # Unmount the USB device
    subprocess.run(["umount", mount_point])

    # Eject the USB device
    subprocess.run(["udisksctl", "power-off", "-b", device])

    # Rename the directory to indicate completion
    os.rename(dest_dir, f"{base_path}/FINISHED-{device}-{current_date}")
else:
    print(f"Device size of {size_tib:.2f} TiB exceeds the limit of {size_limit} TiB. No action taken.")
