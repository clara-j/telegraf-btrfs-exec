# telegraf-btrfs-exec
Python script that can be used to capture BTRFS information in telegraf

# Usage
1. Install and place btrfs.read.py in location accessible by telgraf.   For example /etc/telegraf/btrfs.read.py
2. Grant telegraf permission to sudo btrfs command without password by adding the following to /etc/sudoers
```
telegraf ALL=(root) NOPASSWD: /usr/local/bin/btrfs
```
3. Update /etc/telegraf/telegraf.conf to call the script
```
 [[inputs.exec]]
   commands = [
     "python /etc/telegraf/btrfs.read.py"
   ]
   timeout = "5s"
   data_format = "influx"
```


# Donation
If you find this usefull and you would like to support please the use option below.

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=jason%2ep%2eclara%40gmail%2ecom&lc=CA&item_name=Jason%20Clara&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted)
