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
