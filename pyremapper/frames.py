import Tkinter
import ttk
import time
import functools

from dialog import *
from joystick import vJoyComponent
from joystick import pygameJoyComponent
from utils import *
from enum import Enum


class vJoyFrame(ttk.Frame):
   def __init__(self, parent, vJoystick, joystick_manager, key_mouse_manager, **kwargs):
      #TK setup
      ttk.Frame.__init__(self, parent, **kwargs)
      self.parent = parent

      self.widget_variables = dict()
      self.frames = list()
      for axis, data in vJoystick.axes.items():
         axis_frame = AxisFrame(
            self,
            vJoystick,
            joystick_manager,
            key_mouse_manager,
            axis,
            text = 'Axis %s' % (joystick_manager.get_axis_index(axis) + 1)
         )
         self.frames.append(axis_frame)
         axis_frame.pack(side = 'top')
      return


class RemapperLabelFrame(ttk.LabelFrame):
   def __init__(self, parent, vJoystick, joystick_manager, key_mouse_manager, axis, **kwargs):
      #TK setup
      ttk.LabelFrame.__init__(self, parent, **kwargs)
      self.parent = parent

      self.axis = axis
      self.vjoy_tuple = (vJoystick.id, vJoyComponent.axis, axis)
      self.widget_variables = dict()
      self.vJoystick = vJoystick
      self.joystick_manager = joystick_manager
      self.key_mouse_manager = key_mouse_manager
      
      self.child_init()
      return

   def child_init(self):
      pass


class AxisFrame(RemapperLabelFrame):
   KEYBOARD_FRAME = 0
   JOYSTICK_FRAME = 1
   MOUSE_FRAME = 2
   
   def child_init(self):
      self.radio_frame = self.create_input_select_radios(self)

      self.frames = list()
      self.frames.append( KeyboardFrame(self, self.vJoystick, self.joystick_manager, self.key_mouse_manager, self.axis, text = 'Keyboard') )
      self.frames.append( JoystickFrame(self, self.vJoystick, self.joystick_manager, self.key_mouse_manager, self.axis, text = 'Joystick') )
      #self.frames.append( MouseFrame(self,    self.vJoystick, self.joystick_manager, self.key_mouse_manager,  self.axis,text = 'Mouse') )
      for index, frame in enumerate(self.frames):
         frame.grid(row = 1, column = index + 2, stick='NEWS')
      self.widget_variables['input_type_radio_var'].set(-1)
      return

   def create_input_select_radios(self, parent):
      radio_frame = ttk.Frame(parent)
      radio_frame.grid(row = 1, column = 1, stick = 'N')

      # Create radio buttons
      self.widget_variables['input_type_radio_var'] = Tkinter.IntVar()
      radio_none = ttk.Radiobutton(radio_frame, text = 'None', variable = self.widget_variables['input_type_radio_var'], value = -1)
      radio_none.grid(row = 1, column = 1, stick='W')
      radio_keyboard = ttk.Radiobutton(radio_frame, text = 'Keyboard', variable = self.widget_variables['input_type_radio_var'], value = self.KEYBOARD_FRAME)
      radio_keyboard.grid(row = 2, column = 1, stick='W')
      radio_joystick = ttk.Radiobutton(radio_frame, text = 'Joystick', variable = self.widget_variables['input_type_radio_var'], value = self.JOYSTICK_FRAME)
      radio_joystick.grid(row = 3, column = 1, stick='W')
      radio_mouse = ttk.Radiobutton(radio_frame, text = 'Mouse', variable = self.widget_variables['input_type_radio_var'], value = self.MOUSE_FRAME, state = DISABLE)
      radio_mouse.grid(row = 4, column = 1, stick='W')
      
      self.widget_variables['input_type_radio_var'].trace('w', self.input_type_radio_changed_callback)
      return radio_frame
      
   @exception_handler
   def input_type_radio_changed_callback(self, *_):
      radio_value = self.widget_variables['input_type_radio_var'].get()
      for index, frame in enumerate(self.frames):
         if radio_value == index:
            set_state_recursive(frame, ENABLE)
            # Enable Hotkeys?
         else:
            # Disable GUI
            set_state_recursive(frame, DISABLE)
            # Disable hotkey(s)
            if index == self.KEYBOARD_FRAME and self.vjoy_tuple in self.key_mouse_manager.hotkeys:
               self.key_mouse_manager.hotkeys[self.vjoy_tuple].clear()
            elif index == self.JOYSTICK_FRAME:
               self.joystick_manager.remove_map(self.vjoy_tuple)
      return


class KeyboardFrame(RemapperLabelFrame):
   __num_keysets = 4

   def child_init(self):
      self.widget_variables['auto_center_checkbutton_var'] = Tkinter.StringVar()
      self.widget_variables['auto_center_value_var'] = Tkinter.StringVar()
      self.widget_variables['keyset'] = Tkinter.IntVar(0)

      self.create_binding_ui()
      self.create_auto_center_ui()
      self.create_keysets_ui()
      return

   def create_binding_ui(self):
      for bind_number in range(2):
         # Bind frame
         binding_frame = ttk.Frame(self)
         binding_frame.grid(row = bind_number + 2, column = 1, stick='W', padx = 20)
         # Variables
         binding_var = Tkinter.StringVar()
         self.widget_variables['binding_%i' % bind_number] = binding_var

         # Bind label
         binding_label_widget = ttk.Label(binding_frame, text = 'N/A', width=25)
         binding_label_widget.pack(side = 'left')
         self.widget_variables['binding_label_widget_%i' % bind_number] = binding_label_widget

         # Create a button widget and bind it to bind_button_callback
         # This will configure the label text and setup the hotkey
         bind_callback = functools.partial(self.bind_button_callback, bind_number)
         button_widget = ttk.Button( binding_frame, text = 'Bind', command = bind_callback )
         button_widget.pack(side = 'left')

         # Label and entry for value
         ttk.Label(binding_frame, text = 'Value').pack(side = 'left')
         ttk.Entry(binding_frame, width = 7, textvariable = binding_var).pack(side = 'left')
         value_callback = functools.partial(self.bind_value_callback, bind_number)
         binding_var.trace('w', value_callback)
      # end for

      return
   
   def create_auto_center_ui(self):
      # Auto center frame
      auto_center_frame = ttk.Frame(self)
      auto_center_frame.grid(row = 5, column = 1, stick='W', padx = 20)
      # Auto center checkbutton widget
      checkbutton = ttk.Checkbutton(
         auto_center_frame,
         text = 'Auto center',
         variable = self.widget_variables['auto_center_checkbutton_var']
      )
      checkbutton.pack(side = 'left')
      # Auto center entry widget
      self.auto_center_widget = ttk.Entry(auto_center_frame, state = DISABLE, width = 5, textvariable = self.widget_variables['auto_center_value_var'] )
      self.auto_center_widget.pack(side = 'left')
      
      # Setup callbacks
      self.widget_variables['auto_center_checkbutton_var'].trace('w', self.auto_center_changed_callback)
      self.widget_variables['auto_center_value_var'].trace('w', self.auto_center_changed_callback)
      return

   def create_keysets_ui(self):
       # Keyset frame
      keyset_frame = ttk.LabelFrame(self, text = 'Keyset')
      keyset_frame.grid(row = 6, column = 1, stick='W', padx = 20)
      ttk.Radiobutton(keyset_frame, text = 'None', value = 0, variable = self.widget_variables['keyset']).grid(row = 1, column = 0)
      for col in range(1, self.__num_keysets + 1):
         keyset = col
         ttk.Radiobutton(keyset_frame, text = keyset, value = keyset, variable = self.widget_variables['keyset']).grid(row = 1, column = col)
      self.widget_variables['keyset'].trace('w', self.keyset_changed_callback)
      return

   def get_keyset(self):
      keyset_value = self.widget_variables['keyset'].get()
      if keyset_value > 0:
         return keyset_value
      else:
         return None

   ################################# Call backs ##################################
   @exception_handler
   def bind_button_callback(self, bind_number):
      binder = Binder(self.parent, self.key_mouse_manager)
      keys_down = binder.value
      text = [ i for i in keys_down ]
      self.widget_variables['binding_label_widget_%i' % bind_number].configure(text = text)
      binding_value_var = self.widget_variables['binding_%i' % bind_number]
      try:
         value = float(binding_value_var.get())
      except ValueError:
         value = 0.0
         binding_value_var.set(value)

      keyset = self.get_keyset()
      self.key_mouse_manager.add_hotkey(keys_down, value, self.vjoy_tuple, bind_number, keyset = keyset)
      # Trigget auto center update
      auto_center_check_var = self.widget_variables['auto_center_checkbutton_var']
      auto_center_check_var.set(auto_center_check_var.get())
      return

   @exception_handler
   def bind_value_callback(self, bind_number, *_):
      binding_value_var = self.widget_variables['binding_%i' % bind_number]
      try:
         value = float(binding_value_var.get())
      except ValueError:
         # Invalid value error
         return

      keyset = self.get_keyset()
      self.key_mouse_manager.update_hotkey(self.vjoy_tuple, bind_number, value = value)
      # Trigget auto center update
      auto_center_check_var = self.widget_variables['auto_center_checkbutton_var']
      auto_center_check_var.set(auto_center_check_var.get())
      return

   @exception_handler
   def auto_center_changed_callback(self, *_):
      is_enabled = self.widget_variables['auto_center_checkbutton_var'].get()
      hotkeys_dict = self.key_mouse_manager.hotkeys.get(self.vjoy_tuple, dict())
      if is_enabled:
         # Enable value widget and set default value
         self.auto_center_widget.state( ENABLE )
         auto_center_value_var = self.widget_variables['auto_center_value_var']
         if not auto_center_value_var.get():
            auto_center_value_var.set('0')
         try:
            value = float(auto_center_value_var.get())
         except ValueError:
            return
         # Create on up hotkeys for any existing hotkeys
         for bind_number, hotkey in hotkeys_dict.items():
            if hotkey.on_up:
               continue
            binding = '%s_up' % bind_number
            keyset = self.get_keyset()
            self.key_mouse_manager.add_hotkey(hotkey.keys, value, self.vjoy_tuple, binding, on_up = True, keyset = keyset)
      else:
         self.auto_center_widget.state( DISABLE )
         # Remove on up hotkeys from the given axis
         for binding, hotkey in hotkeys_dict.items():
            if hotkey.on_up:
               self.key_mouse_manager.remove_hotkey(self.vjoy_tuple, binding)
      return

   @exception_handler
   def keyset_changed_callback(self, *_):
      keyset = self.get_keyset()
      self.key_mouse_manager.update_hotkeys(self.vjoy_tuple, keyset = keyset)
      return


class JoystickFrame(RemapperLabelFrame):
   def child_init(self):
      self.joy_id_widget      = None
      self.joy_axis_widget    = None
      self.joy_method_widget  = None

      self.widget_variables['joystick_id'] = Tkinter.StringVar()
      self.widget_variables['joystick_axis'] = Tkinter.StringVar()
      self.widget_variables['joystick_method'] = Tkinter.StringVar()
      self.widget_variables['joystick_deadzone'] = Tkinter.StringVar()
      self.widget_variables['joystick_maxzone'] = Tkinter.StringVar()
      self.widget_variables['joystick_inverted'] = Tkinter.IntVar()

      self.create_joystick_select_ui()
      self.create_options_ui()
      #self.create_feedback_ui()

      # Setup callbacks
      self.widget_variables['joystick_id'].trace('w', self.joystick_id_changed_callback)
      self.widget_variables['joystick_axis'].trace('w', self.joystick_widget_changed_callback)
      self.widget_variables['joystick_method'].trace('w', self.joystick_widget_changed_callback)
      self.widget_variables['joystick_deadzone'].trace('w', self.joystick_widget_changed_callback)
      self.widget_variables['joystick_maxzone'].trace('w', self.joystick_widget_changed_callback)
      self.widget_variables['joystick_inverted'].trace('w', self.joystick_widget_changed_callback)
      return

   def create_joystick_select_ui(self):
      joystick_select_frame = ttk.Frame(self)
      joystick_select_frame.grid(row = 1, column = 1, stick='W', padx = 20)
      # Joystick ID
      ttk.Label(joystick_select_frame, text = 'Joy ID').grid( row = 1, column = 1)
      # Get the list of joystick names
      joystick_names  = ['%i - %s' % (joy.get_id(), joy.get_name()) for joy in self.joystick_manager.pygame_joysticks.values()]
      joy_id_widget = ttk.Combobox(joystick_select_frame, width = 25, values = joystick_names, textvariable = self.widget_variables['joystick_id'])
      joy_id_widget.grid( row = 1, column = 2)
      # Joystick Axis Widget
      ttk.Label(joystick_select_frame, text = 'Joy Axis').grid( row = 1, column = 3)
      joy_axis_widget = ttk.Combobox(joystick_select_frame, width = 3, textvariable = self.widget_variables['joystick_axis'])
      joy_axis_widget.grid( row = 1, column = 4)
      self.joy_id_widget = joy_id_widget
      self.joy_axis_widget = joy_axis_widget
      return
      
   def create_options_ui(self):
      frame = ttk.LabelFrame(self, text = 'Options')
      frame.grid(row = 2, column = 1)
      ttk.Label(frame, text = 'Method').grid( row = 1, column = 1)
      joy_method_widget = ttk.Combobox(
         frame,
         values = self.joystick_manager.mapping_functions.keys(),
         textvariable = self.widget_variables['joystick_method'],
      )
      joy_method_widget.grid( row = 1, column = 2)
      joy_method_widget.current(0)
      self.joy_method_widget = joy_method_widget
      
      # Joystick deadzone
      ttk.Label(frame, text = 'Deadzone').grid(row = 2, column = 1, pady = 5)
      ttk.Entry(frame, width = 7, textvariable = self.widget_variables['joystick_deadzone']).grid(row = 2, column = 2, pady = 5, stick = 'W')
      self.widget_variables['joystick_deadzone'].set('.05')
      
      # Joystick maxzone
      ttk.Label(frame, text = 'Maxzone').grid(row = 3, column = 1, pady = 5)
      ttk.Entry(frame, width = 7, textvariable = self.widget_variables['joystick_maxzone']).grid(row = 3, column = 2, pady = 5, stick = 'W')
      self.widget_variables['joystick_maxzone'].set('.98')
      

      # Joystick invert widget
      ttk.Label(frame, text = 'Invert?').grid(row = 4, column = 1)
      invert_widget = ttk.Checkbutton(frame, text = '', variable = self.widget_variables['joystick_inverted'])
      invert_widget.grid(row = 4, column = 2, stick = 'W')
      return
      
   def create_feedback_ui(self):
      feedback_frame = ttk.Frame(self)
      feedback_frame.grid(row = 2, column = 1, stick='W', padx = 20)
      ttk.Label(feedback_frame, text = 'Input').grid( row = 1, column = 1)
      scale_input = ttk.Scale(feedback_frame, from_ = -1, to = 1)
      scale_input.grid(row = 2, column = 1, padx = 5)
      ttk.Label(feedback_frame, text = 'Output').grid( row = 1, column = 2)
      ttk.Scale(feedback_frame, from_ = -1, to = 1).grid(row = 2, column = 2, padx = 5)
      return

   ################################# Call backs ##################################
   @exception_handler
   def joystick_id_changed_callback(self, *_):
      value = self.joy_id_widget.current()
      self.joy_axis_widget.state(ENABLE)
      joystick = self.joystick_manager.pygame_joysticks[value]
      self.joy_axis_widget.configure( values = range(joystick.get_numaxes()) )
      return

   @exception_handler
   def joystick_widget_changed_callback(self, *_):
      if self.joy_id_widget.current() < 0:
         return
      elif self.joy_axis_widget.current() < 0:
         return

      data = {
         'pygame_id': self.joy_id_widget.current(),
         'pygame_component': pygameJoyComponent.axis,
         'pygame_component_id': self.joy_axis_widget.current(),
         'mapping_func_offset': self.joy_method_widget.current(),
         'joystick_inverted': self.widget_variables['joystick_inverted'].get(),
      }
      try:
         data['joystick_deadzone'] = float( self.widget_variables['joystick_deadzone'].get() )
         data['joystick_maxzone'] = float( self.widget_variables['joystick_maxzone'].get() )
      except ValueError:
         data['joystick_deadzone'] = 0.0
         data['joystick_maxzone'] = 1.0
      
      self.joystick_manager.update_map(self.vjoy_tuple, **data)
      return


class MouseFrame(RemapperLabelFrame):
   def child_init(self):
      mouse_options_frame = ttk.LabelFrame(self)
      mouse_options_frame.grid(row = 1, column = 4, stick='N')

      option_frame = ttk.Frame(mouse_options_frame)
      option_frame.grid(row = 2, column = 1, columnspan = 5, stick='W', padx = 20)

      ttk.Label(option_frame, text = 'Mouse Axis').pack(side = 'left')
      ttk.Combobox(option_frame, width = 5, values = ('', 'X', 'Y', 'Wheel')).pack(side = 'left')
      return
