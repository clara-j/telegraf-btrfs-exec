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

# Example output
```
btrfs_stat,pool=/,drive=/dev/mapper/luks-0ff56354-f5c9-45b2-852c-a456641e5722 write_io_errs=0,read_io_errs=0,flush_io_errs=0,corruption_errs=0,generation_errs=0
btrfs_df,type=Data,raidType=single,pool=/ total=30073159680,used=27799445504,free=2273714176
btrfs_df,type=System,raidType=single,pool=/ total=4194304,used=16384,free=4177920
btrfs_df,type=Metadata,raidType=single,pool=/ total=2155872256,used=1173159936,free=982712320
btrfs_df,type=GlobalReserve,raidType=single,pool=/ total=79544320,used=0,free=79544320
btrfs_usage,pool=/ device_size=254339448832,device_allocated=32233226240,device_unallocated=222106222592,device_missing=0,used=28972621824,free_estimated=224379936768,free_statfs=224378888192,data_ratio=1.00,metadata_ratio=1.00,global_reserve=79544320,multiple_profiles=no
btrfs_usage,pool=/,drive=/dev/mapper/luks-0ff56354-f5c9-45b2-852c-a456641e5722 Data=30073159680,Metadata=2155872256,System=4194304,Unallocated=222106222592
btrfs_scrub,pool=/ data_extents_scrubbed=0,tree_extents_scrubbed=0,data_bytes_scrubbed=0,tree_bytes_scrubbed=0,read_errors=0,csum_errors=0,verify_errors=0,no_csum=0,csum_discards=0,super_errors=0,malloc_errors=0,uncorrectable_errors=0,unverified_errors=0,corrected_errors=0,last_physical=0
btrfs_stat,pool=/home,drive=/dev/mapper/luks-0ff56354-f5c9-45b2-852c-a456641e5722 write_io_errs=0,read_io_errs=0,flush_io_errs=0,corruption_errs=0,generation_errs=0
btrfs_df,type=Data,raidType=single,pool=/home total=30073159680,used=27799445504,free=2273714176
btrfs_df,type=System,raidType=single,pool=/home total=4194304,used=16384,free=4177920
btrfs_df,type=Metadata,raidType=single,pool=/home total=2155872256,used=1173159936,free=982712320
btrfs_df,type=GlobalReserve,raidType=single,pool=/home total=79544320,used=0,free=79544320
btrfs_usage,pool=/home device_size=254339448832,device_allocated=32233226240,device_unallocated=222106222592,device_missing=0,used=28972621824,free_estimated=224379936768,free_statfs=224378888192,data_ratio=1.00,metadata_ratio=1.00,global_reserve=79544320,multiple_profiles=no
btrfs_usage,pool=/home,drive=/dev/mapper/luks-0ff56354-f5c9-45b2-852c-a456641e5722 Data=30073159680,Metadata=2155872256,System=4194304,Unallocated=222106222592
btrfs_scrub,pool=/home data_extents_scrubbed=0,tree_extents_scrubbed=0,data_bytes_scrubbed=0,tree_bytes_scrubbed=0,read_errors=0,csum_errors=0,verify_errors=0,no_csum=0,csum_discards=0,super_errors=0,malloc_errors=0,uncorrectable_errors=0,unverified_errors=0,corrected_errors=0,last_physical=0
```

# Usage
1. Install and place btrfs.read.py in location accessible by telgraf.   For example /etc/telegraf/btrfs.read.py
2. Grant telegraf permission to sudo btrfs command without password by adding a line similar to the following to /etc/sudoers
```
telegraf ALL=(root) NOPASSWD: /usr/bin/btrfs filesystem df *, /usr/bin/btrfs device stat *, /usr/bin/btrfs filesystem usage *, /usr/bin/btrfs scrub status *
```
You can discover the proper btrfs location by issuing `command -v btrfs` on your system.

3. Update /etc/telegraf/telegraf.conf to call the script
```
 [[inputs.exec]]
   commands = [
     "python3 /etc/telegraf/btrfs.read.py"
   ]
   timeout = "5s"
   data_format = "influx"
```

# Requirements
* python3
* btrfs-tools
