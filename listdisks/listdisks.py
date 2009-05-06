#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dbus
import pdb

def discover():
	disks = []
	volumes = []
	
	# get a connection to the system bus
	bus = dbus.SystemBus ()
	
	
	# get a HAL object and an interface to HAL to make function calls
	hal_obj = bus.get_object ('org.freedesktop.Hal',
				  '/org/freedesktop/Hal/Manager')
	hal = dbus.Interface (hal_obj, 'org.freedesktop.Hal.Manager')
	
	# find all devices that have the capability 'volume'
	udis = hal.FindDeviceByCapability('volume')

	for udi in udis:
		# get volume info
		dev_obj = bus.get_object('org.freedesktop.Hal', udi)
		dev = dbus.Interface(dev_obj, 'org.freedesktop.Hal.Device')
		volume = str(dev.GetProperty('block.device'))
		volume_label = str(dev.GetProperty('volume.label'))
		volume_mount_point = str(dev.GetProperty('volume.mount_point'))
		volume_fstype = str(dev.GetProperty('volume.fstype'))
		
		# get storage info
		parent_udi = dev.GetProperty('info.parent')
		dev_obj = bus.get_object('org.freedesktop.Hal', parent_udi)
		dev = dbus.Interface(dev_obj, 'org.freedesktop.Hal.Device')
		storage = str(dev.GetProperty('block.device'))
		storage_product = str(dev.GetProperty('info.product'))
		
		# filter out hard disks
		if dev.GetProperty('storage.drive_type') != 'disk':
			continue

		# store disk
		if disks==[]:
			disks.append((storage,storage_product))		
		else:		
			for i in range(0,(len(disks))):
				finded=False
				if  storage in disks[i]:
					finded=True
				if finded==False and i==(len(disks)-1):
					disks.append((storage,storage_product))
		
		# store volume
		volumes.append((storage,
			volume,
			volume_label,
			volume_mount_point,
			volume_fstype))

	return disks, volumes

if __name__ == '__main__':
    disks, volumes = discover()

    for disk in disks:
        print 'found disk', disk

        for volume in volumes:
            if volume[0] == disk:
                print '    with volume', volume[1]
                print '        label', volume[2]
                print '        mount point is', volume[3]
                print '        fstype is', volume[4]
