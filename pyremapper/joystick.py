import threading
import time
import pygame
from collections import OrderedDict

from vjoy import *
from enum import Enum

vJoyComponent = Enum([
   'axis',
   'button',
   'discrete',
   'continuous',
])

pygameJoyComponent = Enum([
   'axis',
   'button',
   'hat',
   'ball',
])

def linear(x):
   return x

class JoystickManager(object):
   __max_vJoysticks = 8
   __HID_OFFSET = 0x30

   def __init__(self, mapping_functions):
      # Initialize pygame
      self.pygame = pygame
      self.pygame.init()
      self.running = False
      self.mappings = dict()
      self.mapping_functions = OrderedDict([
         ('Linear', linear),
      ])
      # Add user mapping functions
      if mapping_functions:
         self.mapping_functions.update( [(map_dict['name'], map_dict['function']) for map_dict in mapping_functions] )

      # Initialize vJoy
      self.vjoy = vJoy()
      for id in range(1, self.__max_vJoysticks+1):
         self.vjoy.acquire_device(id)

      self.pygame_joysticks = dict()
      self.num_pygame_joysticks = pygame.joystick.get_count()
      for id in range(0, self.num_pygame_joysticks):
         self.pygame_joysticks[id] = pygame.joystick.Joystick(id)
         self.pygame_joysticks[id].init()
      return

   def update_map(self, vjoy_tuple, **kwargs):
      mapping_func_names = self.mapping_functions.keys()
      kwargs['mapping_func_name'] = mapping_func_names[kwargs['mapping_func_offset']]
      self.mappings[vjoy_tuple] = kwargs
      return

   def remove_map(self, vjoy_tuple):
      if vjoy_tuple in self.mappings:
         self.mappings.pop(vjoy_tuple)
      return

   def run_map(self, vjoy_tuple, **kwargs):
      if kwargs['pygame_component'] == pygameJoyComponent.axis:
         pygame_value = self.pygame_joysticks[kwargs['pygame_id']].get_axis(kwargs['pygame_component_id'])
         if kwargs['joystick_inverted']:
            pygame_value = pygame_value * -1
         pygame_value = self.mapping_functions[kwargs['mapping_func_name']](pygame_value)
         # Make values in bounds
         if pygame_value > 1.0:
            pygame_value = 1.0
         elif pygame_value < -1.0:
            pygame_value = -1.0
      else:
         return False
      self.set_component_value(*(vjoy_tuple + (pygame_value,)))
      return

   def set_component_value(self, vjoy_id, vjoy_component, vjoy_component_id, value):
      vJoystick = self.get_vJoystick(vjoy_id)
      if vjoy_component == vJoyComponent.axis:
         vJoystick.set_axis(vjoy_component_id, value)
      return

   def quit(self):
      self.running = False
      self.vjoy.quit()
      self.pygame.quit()
      return
      
   def get_axis_index(self, HID):
      return (HID - self.__HID_OFFSET)

   def get_hid_value(self, axis_index):
      return (axis_index + self.__HID_OFFSET)

   def get_vJoystick(self, id):
      return self.vjoy.vjoy_devices[id]

   def get_vJoysticks(self):
      return self.vjoy.vjoy_devices

   def get_pygame_joysticks(self):
      return self.pygame_joysticks

   def pump(self):
      while self.running:
         pygame.event.pump()
         self.vjoy.pump()
         for vjoy_tuple, data in self.mappings.items():
            self.run_map(vjoy_tuple, **data)
         time.sleep(.01)
      return

   def start(self):
      self.running = True
      self.thread = threading.Thread(target = self.pump)
      self.thread.daemon = True
      self.thread.start()
      return

if __name__ == '__main__':
   JoystickManager()
