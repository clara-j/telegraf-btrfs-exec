# telegraf-btrfs-exec
Python script that can be used to capture BTRFS information in telegraf

# What does it capture
Currently it captures the following information for all the pools mounted at the time of running

## $btrfs device stat
* write_io_errs (per device)
* read_io_errs (per device)
* flush_io_errs (per device)
* corruption_errs (per device)
* generation_errs (per device)

## $btrfs filesystem df
* Data (total, used, free)
* System (total, used, free)
* Metadata (total, used, free)
* GlobalReserve (total, used, free)

## $btrfs filesystem usage
* device_size
* device_allocated
* device_unallocated
* device_missing
* used
* free_estimated
* free_statfs (btrfs-progs >= 5.10)
* data_ratio
* metadata_ratio
* global_reserve
* data (Per Device)
* metadata (Per Device)
* system (Per Device)
* unallocated (Per Device)

## $btrfs scrub status
* time_taken
* data_extents_scrubbed
* tree_extents_scrubbed
* data_bytes_scrubbed
* tree_bytes_scrubbed
* read_errors
* csum_errors
* verify_errors
* no_csum
* csum_discards
* super_errors
* malloc_errors
* uncorrectable_errors
* unverified_errors
* corrected_errors
* last_physical

# Usage
1. Install and place btrfs.read.py in location accessible by telgraf.   For example /etc/telegraf/btrfs.read.py
2. Grant telegraf permission to sudo btrfs command without password by adding a line similar to the following to /etc/sudoers
```
telegraf ALL=(root) NOPASSWD: /usr/bin/btrfs filesystem df *, /usr/bin/btrfs device stat *, /usr/bin/btrfs filesystem usage *
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
* python3
* btrfs-tools

# Donation
If you find this useful and you would like to support please the use option below.

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=jason%2ep%2eclara%40gmail%2ecom&lc=CA&item_name=Jason%20Clara&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted)
