# telegraf-btrfs-exec
Python script that can be used to capture BTRFS information in telegraf

# What does it capture
Currently it captures the following information for all the pools mounted at the time of running

## $btrfs device stat
* write_io_errs
* read_io_errs
* flush_io_errs
* corruption_errs
* generation_errs

## $btrfs filesystem df
* Data (total, used, free)
* System (total, used, free)
* Metadata (total, used, free)
* GlobalReserve (total, used, free)

## $btrfs filesystem usage
* Device_size
* Device_allocated
* Device_unallocated
* Device_missing
* Used
* Free_(estimated)
* Data_ratio
* Metadata_ratio
* Global_reserve
* Data (Per Device)
* Metadata (Per Device)
* System (Per Device)
* Unallocated (Per Device)


# Usage
1. Install and place btrfs.read.py in location accessible by telgraf.   For example /etc/telegraf/btrfs.read.py
2. Grant telegraf permission to sudo btrfs command without password by adding a line similar to the following to /etc/sudoers
```
telegraf  ALL=(root) NOPASSWD: /usr/bin/btrfs filesystem df *, /usr/bin/btrfs device stat *, /usr/bin/btrfs filesystem usage *
```
You can discover the proper btrfs location by issuing `command -v btrfs` on your system.

3. Update /etc/telegraf/telegraf.conf to call the script
```
 [[inputs.exec]]
   commands = [
     "python /etc/telegraf/btrfs.read.py"
   ]
   timeout = "5s"
   data_format = "influx"
```

# Requirements
* python
* btrfs-tools

# Donation
If you find this usefull and you would like to support please the use option below.

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=jason%2ep%2eclara%40gmail%2ecom&lc=CA&item_name=Jason%20Clara&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted)
