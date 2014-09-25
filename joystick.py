import threading
import time
import pygame
from vjoy import *


class JoystickManager:
   __max_vJoysticks = 8

   def __init__(self):
      # Initialize pygame
      self.pygame = pygame
      self.pygame.init()
      self.running = False
      self.maps = dict( [(id, dict()) for id in range(1, self.__max_vJoysticks+1)] )

      # Initialize vJoy
      self.vjoy = vJoy()
      for id in range(1, self.__max_vJoysticks+1):
         self.vjoy.acquire_device(id)

      self.joysticks = dict()
      self.num_joysticks = pygame.joystick.get_count()
      for id in range(0, self.num_joysticks):
         self.joysticks[id] = pygame.joystick.Joystick(id)
         self.joysticks[id].init()
      return

   def add_map(self, vjoy_id, vjoy_axis, pygame_id, pygame_axis, mapping_func = None):
      self.maps[vjoy_id][vjoy_axis] = (pygame_id, pygame_axis, mapping_func)
      return

   def remove_map(self, vjoy_id, vjoy_axis):
      self.maps[vjoy_id][vjoy_axis] = None
      return

   def map_joystick(self, vjoy_id, vjoy_axis, pygame_id, pygame_axis, mapping_func):
      axis_value = self.joysticks[pygame_id].get_axis(pygame_axis)
      if mapping_func is not None:
         axis_value = mapping_func(axis_value)
      vJoystick = self.get_vJoystick(vjoy_id)
      vJoystick.set_axis(vjoy_axis, axis_value)
      return

   def quit(self):
      self.running = False
      self.vjoy.quit()
      self.pygame.quit()
      return

   def get_vJoystick(self, id):
      return self.vjoy.get_device(id)

   def get_vJoysticks(self):
      return self.vjoy._devices

   def get_joysticks(self):
      return self.joysticks

   def pump_loop(self):
      while self.running:
         pygame.event.pump()
         self.vjoy.pump()
         for vjoy_id, vjoy_axis_dict in self.maps.items():
            for vjoy_axis, data in vjoy_axis_dict.items():
               if data is not None:
                  self.map_joystick(vjoy_id, vjoy_axis, *data)
         time.sleep(.01)
      return

   def pump(self):
      self.running = True
      self.thread = threading.Thread(target = self.pump_loop)
      self.thread.daemon = True
      self.thread.start()
      return

if __name__ == '__main__':
   JoystickManager()
