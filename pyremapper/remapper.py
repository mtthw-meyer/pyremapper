import Tkinter
import ttk
import time
import multiprocessing

from joystick import *
from keymouse import *
from frames import *
from mappingmanager import MappingManager
from tools import *


class Remapper(Tkinter.Tk):
   PUMP_DELAY = 10

   def __init__(self, parent = None, settings = 'joystick_remapper.ini', mapping_functions = None):
      #TK setup
      Tkinter.Tk.__init__(self, parent)
      self.parent = parent
      self.title('Joystick Remapper')

      self.settings = settings

      self.mapping_functions = mapping_functions
      self.key_mouse_manager = KeyMouseManager()
      self.joystick_manager = JoystickManager()
      self.joystick_manager.start()
      self.key_mouse_daemon = None
      
      self.mapping_manager = MappingManager(self.key_mouse_manager, self.joystick_manager)

      self.initialize()
      return

   def load(self):
      try:
         f = open(self.settings, 'r')
         for line in f.readlines():
            pass
         f.close()
      except IOError:
         print 'No settings file found, using default settings'
      return

   def save(self):
      f = open(self.settings, 'w')
      # Write stuff
      f.close()

   def initialize(self):
      self.create_menubar()

      self.notebook = ttk.Notebook(self)
      self.notebook.pack(fill='both', expand='yes', padx=5, pady=5)
      # For each vJoystick create a tab
      for vJoy_id, vJoystick in self.joystick_manager.get_vJoysticks().items():
         frame = JoystickFrame(vJoystick, self.joystick_manager, self.key_mouse_manager, self)
         frame.pack()
         self.notebook.add(frame, text='Virtual Joystick %s' % vJoy_id)

   def create_menubar(self):
      # Create the root menu, adding it to self
      self.menu = Tkinter.Menu(self)

      # File menu
      file_menu = Tkinter.Menu(self, tearoff = 0)
      file_menu.add_command(label = 'Load', command = self.mapping_manager.load)
      file_menu.add_command(label = 'Save', command = self.mapping_manager.save)
      file_menu.add_command(label = 'Clear all', command = self.clear)
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
      
   def ask_open(self):
      file_name = tkFileDialog.askopenfilename()
      self.load(file_name)
      
   def clear(self):
      pass

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

   def destroy(self):
      self.joystick_manager.quit()
      if self.key_mouse_daemon is not None:
         self.key_mouse_daemon.terminate()
         self.key_mouse_daemon.join()
      Tkinter.Tk.destroy(self)
      return


if __name__ == '__main__':
   import pdb
   remapper = Remapper()
   remapper.start()
