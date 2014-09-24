#!/usr/bin/python
import Tkinter
import ttk
import time
import multiprocessing

from joystick import *
from keymouse import *
from frames import *
from tools import *


class Remapper(Tkinter.Tk):
   PUMP_DELAY = 10

   def __init__(self, parent = None):
      #TK setup
      Tkinter.Tk.__init__(self, parent)
      self.parent = parent
      self.title('Joystick Remapper')

      self.key_mouse_manager = KeyMouseManager()
      self.joystick_manager = JoystickManager()
      self.joystick_manager.start()
      self.key_mouse_daemon = None

      self.initialize()
      return

   def destroy(self):
      self.joystick_manager.quit()
      if self.key_mouse_daemon is not None:
         self.key_mouse_daemon.terminate()
         self.key_mouse_daemon.join()
      Tkinter.Tk.destroy(self)
      return

   def initialize(self):
      self.create_menubar()

      self.notebook = ttk.Notebook(self, height=1024, width=1024)
      self.notebook.pack()
      # For each vJoystick create a tab
      for vJoy_id, vJoystick in self.joystick_manager.get_vJoysticks().items():
         frame = JoystickFrame(vJoystick, self.joystick_manager, self.key_mouse_manager)
         frame.pack()
         self.notebook.add(frame, text='Virtual Joystick %s' % vJoy_id)

   def create_menubar(self):
      # Create the root menu, adding it to self
      self.menu = Tkinter.Menu(self)

      # File menu
      file_menu = Tkinter.Menu(self, tearoff = 0)
      file_menu.add_command(label = 'Quit', command = self.destroy)
      self.menu.add_cascade(label = 'File', menu = file_menu)

      # Tools menu
      tools_menu = Tkinter.Menu(self, tearoff = 0)
      tools_menu.add_command(label = 'Windows Joystick Manager', command = winjoy)
      tools_menu.add_command(label = 'vJoy Monitor', command = vJoyMonitor)
      tools_menu.add_command(label = 'vJoy Configure', command = vJoyConf)
      self.menu.add_cascade(label = 'Tools', menu = tools_menu)

      # Display the menu
      self.config(menu = self.menu)

   def pump(self):
      self.key_mouse_manager.pump()
      self.joystick_manager.pump()
      # Reregister event callback because Tk is stupid
      self.after(self.PUMP_DELAY, self.pump)
      #if self.state() != 'normal':
       #  print self.state()
      return
      
   def update_thread(self):
      thread = threading.Thread(target = self.update_me)
      thread.daemon = True
      thread.start()
      return
   
   def update_me(self):
      while not self.has_focus:
         self.update()
         time.sleep(0.05)
      return

   def start(self):
      self.key_mouse_daemon = multiprocessing.Process(target = self.key_mouse_manager.pump)
      self.key_mouse_daemon.start()
      self.mainloop()
      return


if __name__ == '__main__':
   import pdb
   remapper = Remapper()
   remapper.start()
