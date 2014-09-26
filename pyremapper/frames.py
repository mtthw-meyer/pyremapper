import Tkinter
import ttk
import time
import functools

from dialog import *
from joystick import vJoyComponent
from joystick import pygameJoyComponent
from utils import *


class JoystickFrame(ttk.Frame):
   def __init__(self, vJoystick, joystick_manager, keyboard_manager, parent = None, **kwargs):
      #TK setup
      ttk.Frame.__init__(self, parent, **kwargs)
      self.parent = parent
      self.tk_variables = dict()

      self.vJoystick = vJoystick
      self.joystick_manager = joystick_manager
      self.keyboard_manager = keyboard_manager
      
      for axis, data in vJoystick.axes.items():
         axis_number = (axis - 0x2F)
         self.tk_variables[axis_number] = dict()
         axis_variables = self.tk_variables[axis_number]

         # Setup Tkinter variables
         axis_variables['input_type_radio'] = Tkinter.StringVar()
         axis_variables['joystick_id'] = Tkinter.StringVar()
         axis_variables['joystick_axis'] = Tkinter.StringVar()
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
      keyboard_options_frame = ttk.LabelFrame(parent)
      keyboard_options_frame.grid(row = 1, column = 2, stick='N')
      variables['frames']['keyboard'] = keyboard_options_frame

      # Create input binds
      for binding_number in range(2):
         # Bind frame
         option_frame = ttk.Frame(keyboard_options_frame)
         option_frame.grid(row = binding_number + 2, column = 1, columnspan = 5, stick='W', padx = 20)
         # Bind label
         bound_button_widget = ttk.Label(option_frame, text = 'N/A', width=25)
         bound_button_widget.pack(side = 'left')
         # Create a button widget and bind it to bind_button_callback
         # This will configure the label text and setup the hotkey
         entry_var = Tkinter.StringVar()
         variables['entry_%i' % binding_number] = entry_var
         
         bind_callback = functools.partial(self.bind_button_callback, bound_button_widget, entry_var, self.vJoystick.id, vJoyComponent.axis, vjoy_axis)
         button_widget = ttk.Button( option_frame, text = 'Bind', command = bind_callback )
         button_widget.pack(side = 'left')
         # Label and entry for value
         ttk.Label(option_frame, text = 'Value').pack(side = 'left')
         ttk.Entry(option_frame, width = 7, textvariable = entry_var).pack(side = 'left')

      # Auto center frame
      auto_center_frame = ttk.Frame(keyboard_options_frame)
      auto_center_frame.grid(row = 5, column = 1, columnspan = 5, stick='W', padx = 20)
      # Auto center checkbutton
      auto_center_checkbutton_var = Tkinter.IntVar()
      variables['auto_center_checkbutton_var'] = auto_center_checkbutton_var
      checkbutton = ttk.Checkbutton(
         auto_center_frame,
         text = 'Auto center',
         variable = auto_center_checkbutton_var
      )
      # Auto center entry
      auto_center_entry_var = Tkinter.StringVar()
      variables['auto_center_entry_var'] = auto_center_entry_var
      entry = ttk.Entry(auto_center_frame, state = DISABLE, width = 5, textvariable = auto_center_entry_var )
      callback = functools.partial(self.auto_center_changed_callback, entry, auto_center_entry_var, auto_center_checkbutton_var)
      auto_center_checkbutton_var.trace('w', callback)

      checkbutton.pack(side = 'left')
      entry.pack(side = 'left')

      return keyboard_options_frame

   def joystick_options(self, parent, variables, vjoy_axis):
      # Create the joystick options frame
      joystick_options_frame = ttk.LabelFrame(parent)
      joystick_options_frame.grid(row = 1, column = 3, stick='N')
      variables['frames']['joystick'] = joystick_options_frame

      option_frame = ttk.Frame(joystick_options_frame)
      option_frame.grid(row = 2, column = 1, columnspan = 5, stick='W', padx = 20)
      # Joystick ID
      ttk.Label(option_frame, text = 'Joy ID').pack(side = 'left')
      # Get the list of joystick names
      joystick_names  = ['%i - %s' % (joy.get_id(), joy.get_name()) for joy in self.joystick_manager.pygame_joysticks.values()]
      # Joystick ID widget
      joy_id_widget = ttk.Combobox(option_frame, width = 20, values = joystick_names, textvariable = variables['joystick_id'])
      joy_id_widget.pack(side = 'left')
      # Joystick Axis Widget
      joy_axis_widget = ttk.Combobox(option_frame, width = 5, state = DISABLE, textvariable = variables['joystick_axis'])
      joy_axis_widget.pack(side = 'left')

      # Changed axes selection based on joystick ID
      
      id_callback = functools.partial(self.joystick_id_changed_callback, joy_id_widget, joy_axis_widget)
      variables['joystick_id'].trace('w', id_callback)

      axis_callback = functools.partial(self.joystick_axis_changed_callback, vjoy_axis, joy_id_widget, joy_axis_widget)
      variables['joystick_axis'].trace('w', axis_callback)

      # Mapping methods
      ttk.Label(option_frame, text = 'TODO: Mapping Method').pack(side = 'left')

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


   def input_type_radio_changed_callback(self, axis_number, *_):
      value = self.tk_variables[axis_number]['input_type_radio'].get()
      for name, widget in self.tk_variables[axis_number]['frames'].items():
         if value == name:
            set_state_recursive(widget, ENABLE)
         else:
            set_state_recursive(widget, DISABLE)
      return


   def bind_button_callback(self, widget, tk_var, vjoy_id, vjoy_comp, vjoy_axis):
      binder = Binder(self.parent, self.keyboard_manager)
      keys_down = binder.value
      vjoy_tuple = (vjoy_id, vjoy_comp, vjoy_axis)
      text = [ i for i in keys_down ]
      widget.configure(text = text)
      value = float(tk_var.get())
      self.keyboard_manager.add_hotkey(vjoy_tuple, value, keys_down)
      return


   def auto_center_changed_callback(self, entry_widget, entry_var, checkbutton_var, *_):
      entry_widget.state( ENABLE if checkbutton_var.get() else DISABLE )
      if not entry_var.get():
         entry_var.set('0')
      return


   def joystick_id_changed_callback(self, id_widget, axis_widget, *_):
      value = id_widget.current()
      axis_widget.state(ENABLE)
      joystick = self.joystick_manager.pygame_joysticks[value]
      axis_widget.configure( values = range(joystick.get_numaxes()) )
      return


   def joystick_axis_changed_callback(self, vjoy_axis, id_widget, axis_widget, *_):
      self.joystick_manager.add_map(
         self.vJoystick.id,
         vJoyComponent.axis,
         vjoy_axis,
         id_widget.current(),
         pygameJoyComponent.axis,
         axis_widget.current(),
         lambda x: x # Joysticks hard coded to linear
      )
      return
