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
from widgets import ScrollingNotebook


class Remapper(Tkinter.Tk):
   PUMP_DELAY = 10
   default_extension = '.keys'

   def __init__(self, parent = None, settings = 'joystick_remapper.ini', mapping_functions = None):
      #TK setup
      Tkinter.Tk.__init__(self, parent)
      self.parent = parent
      self.title('Joystick Remapper')

      self.settings = settings
      self.mapping_functions = mapping_functions
      self.hotkeys_filename = None

      self.joystick_manager = JoystickManager(mapping_functions)
      self.joystick_manager.start()
      self.key_mouse_manager = KeyMouseManager(self.joystick_manager)
      self.key_mouse_daemon = None

      self.initialize()
      return

   def load_settings(self):
      try:
         f = open(self.settings, 'r')
         settings = dict([ [item.strip() for item in line.split('=')] for line in f.readlines() ])
         f.close()
      except IOError:
         print 'No settings file found, using default settings'
         return

      self.geometry(settings['Window'])
      return

   def save_settings(self):
      f = open(self.settings, 'w')
      f.write('Window = %s' % self.geometry())
      f.close()

   def initialize(self):
      self.load_settings()
      self.create_menubar()
      
      # Resize Behavior
      self.grid_rowconfigure(0, weight=1)
      self.grid_columnconfigure(0, weight=1)

      self.notebook = ScrollingNotebook(self)
      self.notebook.frame.grid(row = 0, column = 0, sticky = 'nsew')
      self.frames = list()
      # For each vJoystick create a tab
      for vJoy_id, vJoystick in self.joystick_manager.get_vJoysticks().items():
         frame = vJoyFrame(self.notebook, vJoystick, self.joystick_manager, self.key_mouse_manager)
         frame.pack()
         self.frames.append(frame)
         self.notebook.add(frame, text='Virtual Joystick %s' % vJoy_id)

      return

   def create_menubar(self):
      # Create the root menu, adding it to self
      self.menu = Tkinter.Menu(self)

      # File menu
      file_menu = Tkinter.Menu(self, tearoff = 0)
      file_menu.add_command(label = 'Load...', command = self.hotkeys_load)
      file_menu.add_command(label = 'Save', command = self.hotkeys_save)
      file_menu.add_command(label = 'Save as...', command = self.hotkeys_save_as)
      file_menu.add_separator()
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

   def start(self):
      self.key_mouse_daemon = multiprocessing.Process(target = pythoncom.PumpMessages)
      self.key_mouse_daemon.start()
      self.mainloop()
      return

   def destroy(self):
      self.save_settings()
      self.joystick_manager.quit()
      if self.key_mouse_daemon is not None:
         self.key_mouse_daemon.terminate()
         self.key_mouse_daemon.join()
      Tkinter.Tk.destroy(self)
      return
      
   def hotkeys_load(self, filename = None):
      if filename is None:
         filename = tkFileDialog.askopenfilename(
            defaultextension = self.default_extension,
            filetypes = (('Hotkey file', self.default_extension),)
         )
         if filename is '':
            return

      self.hotkeys_filename = filename

      # Load pickle
      with open(filename, 'rb') as pickle_file:
         data = pickle.load(pickle_file)
         self.key_mouse_manager.hotkeys = data.get(('key_mouse_manager_hotkeys'), dict())
         self.key_mouse_manager.keysets = data.get(('key_mouse_manager_keysets'), dict())
         # Save to local variable, joystick mappings setup by the UI triggers
         mappings = data.get(('joystick_manager_mappings'), dict())

      # Setup loaded hotkeys UI settings
      for vjoy_tuple, hotkey_dict in self.key_mouse_manager.hotkeys.items():
         # Setup variables
         vjoy_id, _, vjoy_axis = vjoy_tuple
         vjoy_frame = self.frames[vjoy_id - 1]
         vjoy_axis_frame = vjoy_frame.frames[self.joystick_manager.get_axis_index(vjoy_axis)]
         keyboard_frame = vjoy_axis_frame.frames[vjoy_axis_frame.KEYBOARD_FRAME]
         # Configure UI
         for binding_number, hotkey in enumerate(hotkey_dict.values()):
            hotkey
            if not hotkey.on_up:
               keyboard_frame.widget_variables['binding_label_widget_%i' % binding_number].configure(text = [k for k in hotkey.keys])
               keyboard_frame.widget_variables['binding_%i' % binding_number].set(hotkey.value)
            else:
               keyboard_frame.widget_variables['auto_center_value_var'].set(hotkey.value)
               keyboard_frame.widget_variables['auto_center_checkbutton_var'].set(True)
            if hotkey.keyset is not None:
               keyboard_frame.widget_variables['keyset'].set(hotkey.keyset)
         vjoy_axis_frame.widget_variables['input_type_radio_var'].set(vjoy_axis_frame.KEYBOARD_FRAME)

      # Setup loaded joystick UI settings
      for vjoy_tuple, data in mappings.items():
         # Setup variables
         vjoy_id, _, vjoy_axis = vjoy_tuple
         vjoy_frame = self.frames[vjoy_id - 1]
         vjoy_axis_frame = vjoy_frame.frames[self.joystick_manager.get_axis_index(vjoy_axis)]
         joystick_frame = vjoy_axis_frame.frames[vjoy_axis_frame.JOYSTICK_FRAME]
         # Configure UI
         joystick_frame.joy_id_widget.current(data['pygame_id'])
         joystick_frame.joy_axis_widget.current(data['pygame_component_id'])
         joystick_frame.widget_variables['joystick_method'].set(data['mapping_func_name'])
         joystick_frame.widget_variables['joystick_deadzone'].set(data['joystick_deadzone'])
         joystick_frame.widget_variables['joystick_maxzone'].set(data['joystick_maxzone'])
         joystick_frame.widget_variables['joystick_inverted'].set(data['joystick_inverted'])
         vjoy_axis_frame.widget_variables['input_type_radio_var'].set(vjoy_axis_frame.JOYSTICK_FRAME)

      return

   def hotkeys_save_as(self):
      filename = tkFileDialog.asksaveasfilename(
         defaultextension = self.default_extension,
         filetypes = (('Hotkey file', self.default_extension),)
      )
      if filename is '':
            return
      self.hotkeys_filename = filename
      self.hotkeys_save(filename = filename)
      return

   def hotkeys_save(self, filename = None):
      if self.hotkeys_filename is None:
         self.hotkeys_save_as()
         return

      f = open(self.hotkeys_filename, 'wb')
      data = {
         ('key_mouse_manager_hotkeys'): self.key_mouse_manager.hotkeys,
         ('key_mouse_manager_keysets'): self.key_mouse_manager.keysets,
         ('joystick_manager_mappings'): self.joystick_manager.mappings,
      }
      pickle.dump(data, f, -1)
      f.close()
      return


if __name__ == '__main__':
   remapper = Remapper()
   remapper.start()
