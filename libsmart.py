#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

#!/usr/bin/env python
import dbus
from os import popen2
class SmartInfo:
	def ScanDisks(self):
		"""
		La funcion devuelve un array con el dispositivo, el fabricante y el serial del discoduro
		"""
		disks=[]
		# get a connection to the system bus
		bus = dbus.SystemBus ()
		# get HAL object and an interface to HAL to make function calls
		hal_obj = bus.get_object ('org.freedesktop.Hal',
                              '/org/freedesktop/Hal/Manager')
		hal = dbus.Interface (hal_obj, 'org.freedesktop.Hal.Manager')
		# find all devices that have the capability 'volume'
		udis = hal.FindDeviceByCapability('volume')
		for udi in udis:
			# get storage info
			dev_obj = bus.get_object('org.freedesktop.Hal', udi)
			dev = dbus.Interface(dev_obj, 'org.freedesktop.Hal.Device')
			parent_udi = dev.GetProperty('info.parent')
			dev_obj = bus.get_object('org.freedesktop.Hal', parent_udi)
			dev = dbus.Interface(dev_obj, 'org.freedesktop.Hal.Device')
			storage = str(dev.GetProperty('block.device'))
			storage_product = str(dev.GetProperty('info.product'))
			storage_serial = str(dev.GetProperty('storage.serial'))
			storage_size = str(dev.GetProperty('storage.size'))
			# filter out hard disks
			if dev.GetProperty('storage.drive_type') != 'disk':
				continue
			# store disk
			if not storage in disks:
				disks.append(storage)
		return disks
if __name__ == '__main__':

	a= SmartInfo()
	print a.ScanDisks()

	


	


