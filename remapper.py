#!/usr/bin/python
import Tkinter
import ttk
import time

from joystick import *
from keymouse import *
from frames import *
from tools import *

def blah(event):
   if event.widget.winfo_name() == 'tk':
      print event.widget.state()
   


class Remapper(Tkinter.Tk):
   PUMP_DELAY = 10

   def __init__(self, parent = None):
      #TK setup
      Tkinter.Tk.__init__(self, parent)
      self.parent = parent
      self.title('Joystick Remapper')
      self.time_to_quit = False

      self.key_mouse_manager = KeyMouseManager()
      self.joystick_manager = JoystickManager()
      self.joystick_manager.pump()

      self.initialize()
      self.bind('<FocusOut>', self.start_pyhook)
      self.bind('<FocusIn>', self.start_tk)

   def start_pyhook(self, event):
      if event.widget.winfo_name() == 'tk':
         print self.focus_get()
         #self.quit()
         #self.key_mouse_manager.pump()
      return

   def start_tk(self, event):
      if event.widget.winfo_name() == 'tk':
         print 'Restart tk'
         print self.focus_get()
      
   def cleanup(self):
      self.destroy()
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
      file_menu.add_command(label = 'Quit', command = self.cleanup)
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

   def start(self):
      # Register event callback
      #self.after(self.PUMP_DELAY, self.pump)
      self.mainloop()


if __name__ == '__main__':
   import pdb
   remapper = Remapper()
   remapper.start()
