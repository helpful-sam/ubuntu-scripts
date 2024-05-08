To have Ubuntu automatically invoke a script every time a device is plugged in, you can use udev rules. This method involves creating a udev rule that will trigger your script whenever a USB device is connected. Here's how to set it up:

# Step 1: Create the Script
Ensure your script is executable and located at a suitable path. For example, place it at /usr/local/bin/usb_copy_script.sh. Make sure to mark it as executable:

    bash
    chmod +x /home/usb-auto-backup.py

Your script should handle checking the device size and name, copying files, and ejecting the device. Ensure it can run with root privileges, as udev will execute it as root.

# Step 2: Create a udev Rule

Open a new rule file in the udev rules directory:

    bash
    sudo nano /etc/udev/rules.d/100-usb-autocopy.rules

Add the following rule to the file:

    plaintext
    ACTION=="add", SUBSYSTEM=="block", ENV{ID_BUS}=="usb", RUN+="/home/usb-auto-backup.py %k"

This rule does the following:

    ACTION=="add": Triggers the rule when a device is added.
    SUBSYSTEM=="block": Applies to block devices (like USB storage devices).
    ENV{ID_BUS}=="usb": Ensures the rule only applies to USB devices.
    RUN+="/usr/local/bin/usb_copy_script.sh %k": Executes your script when a USB block device is connected. %k is replaced by the kernel name of the device (e.g., sdb).

Reload the udev rules to apply the new rule:

    bash
    sudo udevadm control --reload-rules
    sudo udevadm trigger

# Step 3: Test the Setup

To test your setup, connect a USB device and check whether the script runs as expected. You might want to add logging to your script to confirm that it is triggered and executes correctly:

    bash
    echo "Device $1 connected" >> /var/log/usb_copy.log

This setup ensures that your script is invoked automatically every time a USB device is plugged into your Ubuntu server. If your script needs to be adjusted for permissions or execution context, you might also consider adding specific user permissions or modifying the script to run as a non-root user, depending on your security requirements.