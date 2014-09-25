import os
from ctypes import cdll

from vjoydevice import *


class vJoyError(Exception):
   pass


VjoyStatus = [
   'VJD_STAT_OWN',   # 0: The  vJoy Device is owned by this application.
	'VJD_STAT_FREE',  # 1: The  vJoy Device is NOT owned by any application (including this one).
	'VJD_STAT_BUSY',  # 2: The  vJoy Device is owned by another application. It cannot be acquired by this application.
	'VJD_STAT_MISS',  # 3: The  vJoy Device is missing. It either does not exist or the driver is down.
	'VJD_STAT_UNKN'   # 4: Unknown   
]


class vJoy:
   __vJoyInterface = None
   vjoy_devices = dict()

   def __init__(self):
      # Setup interface to the vJoy library
      if self.__vJoyInterface is None:
         try:
            self.__vJoyInterface = cdll.LoadLibrary(os.path.join('c:\\Program Files\\vJoy', 'vJoyInterface'))
         except OSError:
            pass

      if self.__vJoyInterface is None:
         try:
            self.__vJoyInterface = cdll.LoadLibrary(os.path.join('c:\\Program Files(x86)\\vJoy', 'vJoyInterface'))
         except OSError:
            pass

      if self.__vJoyInterface is None:
         try:
            self.__vJoyInterface = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), 'vJoyInterface'))
         except OSError:
            pass

      if self.__vJoyInterface is None:
         raise vJoyError('Failed to load the vJoy library(dll) file')

      # Check if a vJoy device is present
      if not self.__vJoyInterface.vJoyEnabled():
         raise  vJoyError('No vJoy device(s) enabled')
      else:
         self.product = cast(self.__vJoyInterface.GetvJoyProductString(), c_wchar_p).value
         self.manufacturer = cast(self.__vJoyInterface.GetvJoyManufacturerString(), c_wchar_p).value
         self.serial = cast(self.__vJoyInterface.GetvJoySerialNumberString(), c_wchar_p).value

      self.vjoyvjoy_devices = dict()
      return

   def __len__(self):
      return len(self.vjoy_devices)

   def __iter__(self):
      return self.vjoy_devices.__iter__()

   def __getitem__(self, id):
      return self.vjoy_devices[id]

   def quit(self):
      for id in self.vjoy_devices.keys():
         self.relinquish_device(id)
      return

   def pump(self):
      for _, device in self.vjoy_devices.items():
         device.update()
      return

   def get_device(self, id):
      return self.vjoy_devices.get(id, None)

   def acquire_device(self, id):
      #VJOYINTERFACE_API BOOL		__cdecl	AcquireVJD(UINT rID);				// Acquire the specified vJoy Device.
      #vjoy_id = c_int(id)
      status = self.__vJoyInterface.GetVJDStatus(id)
      if VjoyStatus[status] == 'VJD_STAT_FREE':
         if self.__vJoyInterface.AcquireVJD(id):
            self.vjoy_devices[id] = vJoyDevice(self.__vJoyInterface, id)
      return self.vjoy_devices.get(id, None)

   def relinquish_device(self, id):
      if id in self.vjoy_devices:
         self.vjoy_devices.pop(id)
      self.__vJoyInterface.RelinquishVJD(id)


if __name__ == '__main__':
   import sys
   import pdb
   import os
   from time import sleep

   device = int(sys.argv[1])
   print 'Loading driver...'
   vjoy = vJoy()
   print 'Success!'
   print 'Trying to load device %s...' % device
   vjoy_1 = vjoy.acquire_device(device)
   print 'Loaded device %s!' % vjoy_1
   sleep(2)
   vjoy_1.set_axis(HID_USAGE_SL1, 0)
   sleep(2)
   vjoy.relinquish_device(device)
   print 'Tests passed!'
   print 'Exiting...'
