import Tkinter
import ttk
import tkFileDialog
import time
import multiprocessing
import pythoncom
import pickle

from joystick import *
from keymouse import *
from frames import *
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

      self.joystick_manager = JoystickManager(mapping_functions)
      self.joystick_manager.start()
      self.key_mouse_manager = KeyMouseManager(self.joystick_manager)
      self.key_mouse_daemon = None

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
      self.frames = list()
      # For each vJoystick create a tab
      for vJoy_id, vJoystick in self.joystick_manager.get_vJoysticks().items():
         frame = JoystickFrame(vJoystick, self.joystick_manager, self.key_mouse_manager, self)
         frame.pack()
         self.frames.append(frame)
         self.notebook.add(frame, text='Virtual Joystick %s' % vJoy_id)

   def create_menubar(self):
      # Create the root menu, adding it to self
      self.menu = Tkinter.Menu(self)

      # File menu
      file_menu = Tkinter.Menu(self, tearoff = 0)
      file_menu.add_command(label = 'Load', command = self.load_hotkeys)
      file_menu.add_command(label = 'Save', command = self.save_hotkeys)
      file_menu.add_command(label = 'Save as', command = self.save_hotkeys)
      file_menu.add_command(label = 'Clear all', command = lambda: self.key_mouse_daemon.terminate())
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
      self.key_mouse_daemon = multiprocessing.Process(target = pythoncom.PumpMessages)
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
      
   def load_hotkeys(self, filename = None):
      if filename is None:
         filename = tkFileDialog.askopenfilename()
         if filename is '':
            return

      # Load pickle
      with open(filename, 'rb') as pickle_file:
         data = pickle.load(pickle_file)
         self.key_mouse_manager.hotkeys = data.get(('key_mouse_manager_hotkeys'), dict())
         self.key_mouse_manager.key_sets = data.get(('key_mouse_manager_keysets'), dict())
         # Save to local variable, joystick mappings setup by the UI triggers
         mappings = data.get(('joystick_manager_mappings'), dict())
         print mappings

      # Setup loaded hotkeys UI settings
      for vjoy_tuple, hotkey_dict in self.key_mouse_manager.hotkeys.items():
         # Setup variables
         vjoy_id, _, vjoy_axis = vjoy_tuple
         axis_index = self.joystick_manager.get_axis_index(vjoy_axis)
         variables = self.frames[vjoy_id - 1].tk_variables[axis_index]
         variables['input_type_radio'].set('keyboard')
         # Configure UI
         binding_number = 0
         for hotkey in hotkey_dict.values():
            if not hotkey.on_up:
               variables['bound_button_widget_%i' % binding_number].configure(text = [k for k in hotkey.keys])
               variables['entry_%i' % binding_number].set(hotkey.value)
               binding_number += 1
            else:
               variables['auto_center_entry_var'].set(hotkey.value)
               variables['auto_center_checkbutton_var'].set(True)
         

      # Setup loaded joystick UI settings
      for vjoy_tuple, pygame_tuple in mappings.items():
         # Setup variables
         vjoy_id, _, vjoy_axis = vjoy_tuple
         axis_index = self.joystick_manager.get_axis_index(vjoy_axis)
         variables = self.frames[vjoy_id - 1].tk_variables[axis_index]
         # Configure UI
         variables['input_type_radio'].set('joystick')
         pygame_id, pygame_component, pygame_axis, mapping_func_name, is_inverted = pygame_tuple
         variables['joystick_id_widget'].current(pygame_id)
         variables['joystick_axis_widget'].current(pygame_axis)
         variables['joystick_method'].set(mapping_func_name)
         variables['invert_axis'].set(is_inverted)

      return

   def save_hotkeys(self, filename = None):
      if filename is None:
         filename = tkFileDialog.asksaveasfilename()
         if filename is '':
            return

      f = open(filename, 'wb')
      data = {
         ('key_mouse_manager_hotkeys'): self.key_mouse_manager.hotkeys,
         ('key_mouse_manager_keysets'): self.key_mouse_manager.keysets,
         ('joystick_manager_mappings'): self.joystick_manager.mappings,
      }
      pickle.dump(data, f, -1)
      f.close()
      print self.joystick_manager.mappings
      return


if __name__ == '__main__':
   remapper = Remapper()
   remapper.start()
