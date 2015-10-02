#!/usr/bin/env python

import sys
import ceph_disk as cdsk

def test_device(device, is_partition):

    errors = 0
    warn   = 0

    devctx = cdsk.get_block_device_ctx(device)
    if devctx:
        print '[PASS] Get Device Context'
    else:
        print '[FAIL] Get Device Context'
        return 1

    """
    Get Device node name
    """
    dev_node = devctx.get_dev_node()
    if dev_node:
        print '[PASS] Get Device Node: %s' %dev_node
    else:
        print '[FAIL] Get Device Node'
        errors+=1

    if is_partition:
        """
        Check if the block device is a partition
        """
        if devctx.is_partition():
            print '[PASS] Partition Test OK'
        else:
            print '[FAIL] Partition Test Fails'
            errors+=1

        """
        Get partition Number
        """
        part_num = devctx.get_partition_num()
        if part_num:
            print '[PASS] Partition Number is %i' %part_num
        else:
            print '[FAIL] Get Partition Number Failed' 

        """
        Return the device path to the partition device corresponding to the
        device partition number
        """
        part_dev = devctx.get_partition_dev(1)
        if part_dev:
            print '[WARN] Get Partition Dev on partition does not Error: %s' %part_dev
            warn += 1
        else:
            print '[PASS] Get Partition Dev Fails as expected'

        """
        Get the underlying base device for a partition
        """
        base_dev = devctx.get_partition_base()
        if base_dev:
            print '[PASS] Base Device is: %s' %base_dev
        else:
            print '[FAIL] Failed to get Base Device'
            errors +=1

        """
        Get list of partitions
        """
        part_list = devctx.list_partitions()
        if part_list:
            print '[WARN] Get Part list OK on partition'
            warn += 1
        else:
            print '[PASS] Get Part list Fails as expected'

        """
        Get Partition TYPE and GUID
        """
        part_type, part_uuid =  devctx.get_partition_guids()
        if part_type:
            print '[PASS] Part Type is: %s' %part_type
        else:
            print '[FAIL] Failed to get part type' 

        if part_uuid:
            print '[PASS] Part UUID is: %s' %part_uuid
        else:
            print '[FAIL] Failed to get part UUID'

    else:
        """
        Check if the block device is a partition
        """
        if devctx.is_partition():
            print '[FAIL] Partition Test Fails'
            errors+=1
        else:
            print '[PASS] Partition Test OK'

        """
        Get partition Number
        """
        part_num = devctx.get_partition_num()
        if part_num:
            print '[FAIL] Partition Number on base device?  %i' %part_num
            errors += 1
        else:
            print '[PASS] No partition number as expected' 

        """
        Return the device path to the partition device corresponding to the
        device partition number
        """
        part_dev = devctx.get_partition_dev(1)
        if part_dev:
            print '[PASS] Get Partition Dev: %s' %part_dev
        else:
            print '[FAIL] Get Partition Dev Fails'
            errors += 1

        """
        Get the underlying base device for a partition
        """
        base_dev = devctx.get_partition_base()
        if base_dev:
            print '[WARN] Base Device on Base?: %s' %base_dev
            warn += 1
        else:
            print '[PASS] Failed to get Base Device as expected'

        """
        Get list of partitions
        """
        part_list = devctx.list_partitions()
        if part_list:
            print '[PASS] Get Part list OK on partition'
            for part in part_list:
                print 'PART: %s' %part
        else:
            print '[WARN] Get Part list Fails, No partitions?'
            warn += 1

        """
        Get Partition TYPE and GUID
        """
        part_type, part_uuid =  devctx.get_partition_guids()
        if part_type:
            print '[WARN] Part Type is: %s' %part_type
            warn += 1
        else:
            print '[PASS] Failed to get part type as expected' 

        if part_uuid:
            print '[PASS] Part UUID is: %s' %part_uuid
            warn += 1
        else:
            print '[PASS] Failed to get part UUID as expected'

    """
    Get list of device holders
    """
    holders = devctx.is_held()
    if holders:
        print 'Print Holder list:'
        for holder in holders:
            print '[HOLDER] %s' %holder
    else:
        print 'Device has no holders'
            
    """
    Classify this device
    """
    dev_type = devctx.get_device_class()
    print 'Device Type is: %s' %dev_type

    """
    Do resync to update OS structures
    """
    devctx.resync_dev_node()

    """
    Get Hardware sector size for the device
    """
    hw_sector_sz = devctx.get_hw_sector_size()
    print 'Hardware Sector Size is: %i' %hw_sector_sz

    if not is_partition:
        free_sz = cdsk.get_largest_free_part_size(device, hw_sector_sz)
        if free_sz:
            print 'Largest Free Partition Size in MB: %d' %free_sz 
        else:
            print 'Unable to Determine largest free part size'

    journal_uuid = '9c9e1134-af8c-4cdb-9db6-d2646fc52340'
    jsymlink = devctx.get_journal_symlink(journal_uuid)
    print 'Journal SymLink is: %s' %jsymlink


    print 'Completed with %i Warnings and %i Errors' %(warn, errors)



if __name__ == '__main__':

    if len(sys.argv) != 3:
        print 'Usage: %s <device> <base|part>'
        sys.exit('usage error') 

    device = sys.argv[1]
    if sys.argv[2] == 'base':
        is_partition = 0
    elif sys.argv[2] == 'part':
        is_partition = 1
    else:
        print 'specify base|part'
        sys.exit('usage error') 

    test_device(device, is_partition)
