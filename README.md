###### Small QOL scripts that I use in my ubuntu instance!

# ISSUES

>### USB-AUTO-BACKUP
>
>>1. udev rule triggers when running '''udevadm test --action=add /dev/sdd''' but does not work when USB is physically plugged in

# SOLVED ISSUES

>### USB-AUTO-BACKUP
>
>>1. udev rule does not trigger when device is connected
>>    - problem: udev rule order was set to 100
>>    - solution: set udev rule order to 60