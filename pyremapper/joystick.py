import threading
import time
import pygame
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


class JoystickManager(object):
   __max_vJoysticks = 8

   def __init__(self):
      # Initialize pygame
      self.pygame = pygame
      self.pygame.init()
      self.running = False
      self.mappings = dict()

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

   def add_map(self, vjoy_id, vjoy_component, vjoy_component_id, pygame_id, pygame_component, pygame_component_id, mapping_func):
      vjoy_tuple = (vjoy_id, vjoy_component, vjoy_component_id)
      self.mappings[vjoy_tuple] = (pygame_id, pygame_component, pygame_component_id, mapping_func)
      return

   def remove_map(self, vjoy_id, vjoy_component, vjoy_component_id):
      vjoy_tuple = (vjoy_id, vjoy_component, vjoy_component_id)
      if vjoy_tuple in self.mappings:
         self.mappings.pop(vjoy_tuple)
      return

   def run_map(self, vjoy_id, vjoy_component, vjoy_component_id, pygame_id, pygame_component, pygame_component_id, mapping_func):
      if pygame_component == pygameJoyComponent.axis:
         pygame_value = self.pygame_joysticks[pygame_id].get_axis(pygame_component_id)
         pygame_value = mapping_func(pygame_value)
      else:
         return False
      self.set_component_value(vjoy_id, vjoy_component, vjoy_component_id, pygame_value)
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
      return (HID - 0x2F)

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
         for vjoy_tuple, pygame_tuple in self.mappings.items():
            self.run_map(*(vjoy_tuple + pygame_tuple))
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
