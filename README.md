# ceph-disk-udev

pyudev based port of ceph-disk utility, uses udev database to classify block
devices and query properties for various ceph operation such as prepare and
activate.

Support for Linux DM multipath is available with the DMBlockDev class and
additional workarounds.


Approach:
========
- Current ceph-disk determines various properties on block device by path
  string manipulations and /sys/dev properties
- These are difficult to implement and fragile for device types such as DM
  multipath
- Since different code needs to be added based on the device type, a Block
  device class based approach has been used
- Based on the device type supplied a block device object is instantiated
  (currently  GenericBlockDev or DMBlockDev)
- Each class implements device specific functionality as an implementation
  of the abstract BlockDevBase base class
    a.  Get partition device from base device
    b.  Get base device from partition
    c.  Get Part UUID and Type
    d.  Determine if device path is partition
    e.  Determine if device is referenced
    f.  Get HW sector size
    g.  List partitions

6.  In Prepare/Activate/List code paths, based on the device object appropriate
    functions for the device get called and these code paths remain clean
7.  Many of the functions are now implemented using the python libudev binding
    via pyudev – this would be more robust than path string based approach

Other Changes
=============

II. Partition creation issues on disks with non 512 byte sectors
1.  Issues are seen when partition are created with all available size or size
    changes due to alignment adjustments
2.  This could be a bug in DM layer, the DM partition nodes do not get created
    if the partition size is not a multiple of the hardware sector size
3.  To overcome this,  partition size creation is always done with absolute
    size(i.e no changes due to start alignment)
4.  Also, to create the data partition, largest available size is determined and
    rounded off to the nearest MB for providing the hw sector size aligned partition size

III. Determining Part UUID and Type
1.  At DM device layer the Part UUID and Type are not available in UDEV DB and
    are not returned by the blkid tool used by ceph-disk
2.  Use of sg-disk utility to obtain this data results in unnecessary change
    events in udev resulting in infinite OSD activation loops
3.  To overcome this, python function to read the GPT table from the device
    and determine the Part type and guid has been added

IV. Disk Activation sequence
1.  OSD and Journal UUID written on the DM device are also available on the
    constituent raw paths, this will result in incorrect OSD activations calls
    on the raw paths
2.  For this,  MPATH specific OSD/JOURNAL type IDs are now used in case of
    multipath devices
3.  Udev Rules for disk partitions type and type.uuid part links creations
    ignore dm-* devices as these are not available in the udev DB for dm devices
4.  Also, ceph OSD activation rules based on part type uuid cannot be run as
    the information is not available at udev
5.  For this a special udev rule is added in the /lib/udev/rules.d path for all
    DM mpath partitions
6.  Ceph-disk now implements a special mpath-activate command which is called
    by the above Udev rule
    a.  Part Type UUID/GUID is read from the disk
    b.  If it is of MAPTH OSD/JOURNAL types  then appropriate OSD activation/journal-activation is launched

V.  kpartx bug for device with non 512 byte sector size.
    Some version of kpartx incorrectly calculate partition sizes with default 512 byte
    sector size. This causes incorrect DM mappings for devices that have higher HW sector
    size (4K).
    https://bugs.launchpad.net/ubuntu/+source/multipath-tools/+bug/1441930
    Please use the version of kpartx with this fix if you intend to deploy DM on
    non 512 byte sector hardware


