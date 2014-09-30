import Tkinter
import ttk
import time
import functools

from dialog import *
from joystick import vJoyComponent
from joystick import pygameJoyComponent
from utils import *
from enum import Enum


class JoystickFrame(ttk.Frame):
   __num_keysets = 4
   def __init__(self, vJoystick, joystick_manager, key_mouse_manager, parent = None, **kwargs):
      #TK setup
      ttk.Frame.__init__(self, parent, **kwargs)
      self.parent = parent
      self.tk_variables = dict()

      self.vJoystick = vJoystick
      self.joystick_manager = joystick_manager
      self.key_mouse_manager = key_mouse_manager
      
      for axis, data in vJoystick.axes.items():
         axis_number = self.joystick_manager.get_axis_index(axis)
         self.tk_variables[axis_number] = dict()
         axis_variables = self.tk_variables[axis_number]

         # Setup Tkinter variables
         axis_variables['input_type_radio'] = Tkinter.StringVar()
         axis_variables['keyset']  = Tkinter.IntVar(0)
         axis_variables['joystick_id'] = Tkinter.StringVar()
         axis_variables['joystick_axis'] = Tkinter.StringVar()
         axis_variables['joystick_method'] = Tkinter.StringVar()
         axis_variables['frames'] = dict()

         # Create the frame for the axis
         axis_frame = ttk.LabelFrame(self, text = 'Axis %s' % axis_number, width = 400)
         axis_frame.pack(side = 'top')         

         # Select input type
         self.input_select_radios(axis_frame, axis_variables)
         self.keyboard_options(axis_frame, axis_variables, axis)
         self.joystick_options(axis_frame, axis_variables, axis)
         self.mouse_options(axis_frame, axis_variables)

         radio_callback = functools.partial(self.input_type_radio_changed_callback, axis_number)
         axis_variables['input_type_radio'].trace('w', radio_callback)
         axis_variables['input_type_radio'].set('none')

      return
      
   def input_select_radios(self, parent, variables):
      radio_frame = ttk.Frame(parent)
      radio_frame.grid(row = 1, column = 1)

      # Create radio buttons
      radio_none = ttk.Radiobutton(radio_frame, text = 'None', variable = variables['input_type_radio'], value = 'none')
      radio_none.grid(row = 1, column = 1, stick='W')
      radio_keyboard = ttk.Radiobutton(radio_frame, text = 'Keyboard/Button', variable = variables['input_type_radio'], value = 'keyboard')
      radio_keyboard.grid(row = 2, column = 1, stick='W')
      radio_joystick = ttk.Radiobutton(radio_frame, text = 'Joystick', variable = variables['input_type_radio'], value = 'joystick')
      radio_joystick.grid(row = 3, column = 1, stick='W')
      radio_mouse = ttk.Radiobutton(radio_frame, text = 'Mouse', variable = variables['input_type_radio'], value = 'mouse', state = DISABLE)
      radio_mouse.grid(row = 4, column = 1, stick='W')
      return radio_frame

   def keyboard_options(self, parent, variables, vjoy_axis):
      vjoy_tuple = (self.vJoystick.id, vJoyComponent.axis, vjoy_axis)
      keyboard_options_frame = ttk.LabelFrame(parent)
      keyboard_options_frame.grid(row = 1, column = 2, stick='N')
      variables['frames']['keyboard'] = keyboard_options_frame

      # Create input binds
      for bind_number in range(2):
         # Bind frame
         option_frame = ttk.Frame(keyboard_options_frame)
         option_frame.grid(row = bind_number + 2, column = 1, columnspan = 5, stick='W', padx = 20)

         # Bind label
         bound_label_widget = ttk.Label(option_frame, text = 'N/A', width=25)
         bound_label_widget.pack(side = 'left')
         variables['bound_button_widget_%i' % bind_number] = bound_label_widget

         # Create a button widget and bind it to bind_button_callback
         # This will configure the label text and setup the hotkey
         axis_value_var = Tkinter.StringVar()
         variables['entry_%i' % bind_number] = axis_value_var
         bind_callback = functools.partial(self.bind_button_callback, bound_label_widget, axis_value_var, variables['keyset'], vjoy_tuple, bind_number)
         button_widget = ttk.Button( option_frame, text = 'Bind', command = bind_callback )
         button_widget.pack(side = 'left')

         # Label and entry for value
         ttk.Label(option_frame, text = 'Value').pack(side = 'left')
         ttk.Entry(option_frame, width = 7, textvariable = axis_value_var).pack(side = 'left')
         value_callback = functools.partial(self.bind_value_callback, axis_value_var, variables['keyset'], vjoy_tuple, bind_number)
         axis_value_var.trace('w', value_callback)
         
      # end for

      # Auto center frame
      auto_center_frame = ttk.Frame(keyboard_options_frame)
      auto_center_frame.grid(row = 5, column = 1, columnspan = 5, stick='W', padx = 20)
      # Auto center checkbutton
      auto_center_checkbutton_var = Tkinter.IntVar(0)
      variables['auto_center_checkbutton_var'] = auto_center_checkbutton_var
      checkbutton = ttk.Checkbutton(
         auto_center_frame,
         text = 'Auto center',
         variable = auto_center_checkbutton_var
      )
      checkbutton.pack(side = 'left')
      # Auto center entry
      auto_center_var = Tkinter.StringVar()
      variables['auto_center_var'] = auto_center_var
      auto_center_widget = ttk.Entry(auto_center_frame, state = DISABLE, width = 5, textvariable = auto_center_var )
      auto_center_widget.pack(side = 'left')

      # Keyset frame
      keyset_frame = ttk.LabelFrame(keyboard_options_frame, text = 'Keyset')
      keyset_frame.grid(row = 6, column = 1, columnspan = 5, stick='W', padx = 20)
      ttk.Radiobutton(keyset_frame, text = 'None', value = 0, variable = variables['keyset']).grid(row = 1, column = 0)
      for col in range(1, self.__num_keysets + 1):
         keyset = col
         ttk.Radiobutton(keyset_frame, text = keyset, value = keyset, variable = variables['keyset']).grid(row = 1, column = col)
      keyset_changed_callback = functools.partial(self.keyset_changed_callback,  variables['keyset'], vjoy_tuple)
      variables['keyset'].trace('w', keyset_changed_callback)

      # Setup callbacks
      auto_center_callback = functools.partial(
         self.auto_center_changed_callback,
         auto_center_widget,
         auto_center_var,
         auto_center_checkbutton_var,
         variables['keyset'],
         vjoy_tuple
      )
      auto_center_checkbutton_var.trace('w', auto_center_callback)
      auto_center_var.trace('w', auto_center_callback)

      return keyboard_options_frame

   def joystick_options(self, parent, variables, vjoy_axis):
      # Create the joystick options frame
      joystick_options_frame = ttk.LabelFrame(parent)
      joystick_options_frame.grid(row = 1, column = 3, stick='N')
      variables['frames']['joystick'] = joystick_options_frame

      option_frame = ttk.Frame(joystick_options_frame)
      option_frame.grid(row = 2, column = 1, columnspan = 5, stick='W', padx = 20)
      # Joystick ID
      ttk.Label(option_frame, text = 'Joy ID').grid( row = 1, column = 1)
      # Get the list of joystick names
      joystick_names  = ['%i - %s' % (joy.get_id(), joy.get_name()) for joy in self.joystick_manager.pygame_joysticks.values()]
      # Joystick ID widget
      joy_id_widget = ttk.Combobox(option_frame, width = 20, values = joystick_names, textvariable = variables['joystick_id'])
      joy_id_widget.grid( row = 1, column = 2)
      # Joystick Axis Widget
      joy_axis_widget = ttk.Combobox(option_frame, width = 5, textvariable = variables['joystick_axis'])
      joy_axis_widget.grid( row = 1, column = 3)
      # Joystick method widget
      method_widget = ttk.Combobox(
         option_frame,
         width = 10,
         values = self.joystick_manager.mapping_functions.keys(),
         textvariable = variables['joystick_method'],
      )
      method_widget.grid( row = 1, column = 4)
      method_widget.current(0)
      # Joystick invert widget
      invert_axis = Tkinter.IntVar()
      variables['invert_axis'] = invert_axis
      invert_widget = ttk.Checkbutton(option_frame, text = 'Invert?', variable = invert_axis)
      invert_widget.grid( row = 2, column = 4)

      # Changed axes selection based on joystick ID
      id_callback = functools.partial(self.joystick_id_changed_callback, joy_id_widget, joy_axis_widget)
      variables['joystick_id'].trace('w', id_callback)
      variables['joystick_id_widget'] = joy_id_widget

      joystick_widget_callback = functools.partial(self.joystick_widget_changed_callback, vjoy_axis, joy_id_widget, joy_axis_widget, method_widget, invert_axis)
      variables['joystick_axis'].trace('w', joystick_widget_callback)
      variables['joystick_method'].trace('w', joystick_widget_callback)
      invert_axis.trace('w', joystick_widget_callback)
      variables['joystick_axis_widget'] = joy_axis_widget

      return joystick_options_frame

   def mouse_options(self, parent, variables):
      mouse_options_frame = ttk.LabelFrame(parent)
      mouse_options_frame.grid(row = 1, column = 4, stick='N')
      variables['frames']['mouse'] = mouse_options_frame

      option_frame = ttk.Frame(mouse_options_frame)
      option_frame.grid(row = 2, column = 1, columnspan = 5, stick='W', padx = 20)

      ttk.Label(option_frame, text = 'Mouse Axis').pack(side = 'left')
      ttk.Combobox(option_frame, width = 5, values = ('', 'X', 'Y', 'Wheel')).pack(side = 'left')

      return mouse_options_frame


###############################################################################
################################# Call backs ##################################
###############################################################################


   @exception_handler
   def input_type_radio_changed_callback(self, axis_number, *_):
      radio_value = self.tk_variables[axis_number]['input_type_radio'].get()
      for name, widget in self.tk_variables[axis_number]['frames'].items():
         if radio_value == name:
            set_state_recursive(widget, ENABLE)
            # Enable Hotkeys?
         else:
            # Disable GUI
            set_state_recursive(widget, DISABLE)
            # Disable hotkey(s)
            vjoy_tuple = (self.vJoystick.id, vJoyComponent.axis, self.joystick_manager.get_hid_value(axis_number))
            if name == 'keyboard' and vjoy_tuple in self.key_mouse_manager.hotkeys:
               self.key_mouse_manager.hotkeys[vjoy_tuple].clear()
            elif name == 'joystick':
               self.joystick_manager.remove_map(vjoy_tuple)
      return

   @exception_handler
   def bind_button_callback(self, widget, value_var, keyset_var, vjoy_tuple, bind_number):
      binder = Binder(self.parent, self.key_mouse_manager)
      keys_down = binder.value
      text = [ i for i in keys_down ]
      widget.configure(text = text)
      try:
         value = float(value_var.get())
      except ValueError:
         value = 0.0
         value_var.set(value)

      keyset = keyset_var.get() if keyset_var.get() > 0 else None
      self.key_mouse_manager.add_hotkey(keys_down, value, vjoy_tuple, bind_number, keyset = keyset)
      print [ (k,v) for k,v in self.key_mouse_manager.hotkeys.items() ]
      return

   @exception_handler
   def bind_value_callback(self, value_var, keyset_var, vjoy_tuple, bind_number, *_):
      try:
         value = float(value_var.get())
      except ValueError:
         # Invalid value error
         return

      keyset = keyset_var.get() if keyset_var.get() > 0 else None
      self.key_mouse_manager.update_hotkey(vjoy_tuple, bind_number, value = value)
      print [ (k,v) for k,v in self.key_mouse_manager.hotkeys.items() ]
      return

   @exception_handler
   def auto_center_changed_callback(self, auto_center_widget, auto_center_var, checkbutton_var, keyset_var, vjoy_tuple, *_):
      is_enabled = checkbutton_var.get()
      hotkeys_dict = self.key_mouse_manager.hotkeys.get(vjoy_tuple, dict())
      if is_enabled:
         # Enable value widget and set default value
         auto_center_widget.state( ENABLE )
         if not auto_center_var.get():
            auto_center_var.set('0')
         try:
            value = float(auto_center_var.get())
         except ValueError:
            return
         # Create on up hotkeys for any existing hotkeys
         for bind_number, hotkey in hotkeys_dict.items():
            if hotkey.on_up:
               continue
            binding = '%s_up' % bind_number
            keyset = keyset_var.get() if keyset_var.get() > 0 else None
            self.key_mouse_manager.add_hotkey(hotkey.keys, value, vjoy_tuple, binding, on_up = True, keyset = keyset)
      else:
         auto_center_widget.state( DISABLE )
         # Remove on up hotkeys from the given axis
         for binding, hotkey in hotkeys_dict.items():
            if hotkey.on_up:
               self.key_mouse_manager.remove_hotkey(vjoy_tuple, binding)
      print [ (k,v) for k,v in self.key_mouse_manager.hotkeys.items() ]
      return
      
   def keyset_changed_callback(self, keyset_var, vjoy_tuple, *_):
      keyset = keyset_var.get() if keyset_var.get() > 0 else None
      self.key_mouse_manager.update_hotkeys(vjoy_tuple, keyset = keyset)
      print [ (k,v) for k,v in self.key_mouse_manager.hotkeys.items() ]
      return

   @exception_handler
   def joystick_id_changed_callback(self, id_widget, axis_widget, *_):
      value = id_widget.current()
      axis_widget.state(ENABLE)
      joystick = self.joystick_manager.pygame_joysticks[value]
      axis_widget.configure( values = range(joystick.get_numaxes()) )
      return

   @exception_handler
   def joystick_widget_changed_callback(self, vjoy_axis, id_widget, axis_widget, method_widget, invert_variable, *_):
      vjoy_tuple = ( self.vJoystick.id, vJoyComponent.axis, vjoy_axis)
      self.joystick_manager.update_map(
         vjoy_tuple,
         id_widget.current(),
         pygameJoyComponent.axis,
         axis_widget.current(),
         method_widget.current(),
         invert_variable.get()
      )
      return
