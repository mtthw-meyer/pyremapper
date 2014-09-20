import Tkinter
import ttk
import time

DISABLE = ('disabled',)
ENABLE = ('!disabled',)


def blah(vJoystick, axis, tk_var):
   print vJoystick.set_axis
   print axis
   print tk_var.get()
   return True


class JoystickFrame(ttk.Frame):
   def __init__(self, vJoystick, joystick_manager, keyboard_manager, parent = None, **kwargs):
      #TK setup
      ttk.Frame.__init__(self, parent, **kwargs)
      self.parent = parent
      self.tk_variables = dict()

      self.vJoystick = vJoystick
      self.joystick_manager = joystick_manager
      self.joysticks = joystick_manager.get_joysticks()
      self.keyboard_manager = keyboard_manager
      
      for axis, data in vJoystick._axes.items():
         axis_number = (axis - 0x2F)
         self.tk_variables[axis_number] = dict()
         axis_variables = self.tk_variables[axis_number]

         # Setup Tkinter variables
         axis_variables['input_type_radio'] = Tkinter.StringVar()
         axis_variables['input_type_radio'].set('keyboard')
         axis_variables['joystick_id'] = Tkinter.StringVar()

         # Create the frame for the axis
         axis_frame = ttk.LabelFrame(self, text = 'Axis %s' % axis_number, width = 400)
         axis_frame.pack(side = 'top')#grid(row = axis_number, column = 1)

         # Select input type
         self.keyboard_options(axis_frame, axis_variables, axis)
         self.joystick_options(axis_frame, axis_variables)
         self.mouse_options(   axis_frame, axis_variables)
         
      return
      
   def bind_button_callback(self, widget, axis, tk_var):
      return
      # While no keys are pressed, wait
      #keys_down = self.keyboard_manager.get_keys_down()
      #text = [ i for i in keys_down ]
      widget.configure(text = text)
      self.keyboard_manager.add_hotkey(
         keys_down,
         #lambda: blah(self.vJoystick, axis, tk_var)
         lambda: self.vJoystick.set_axis(axis, float(tk_var.get()))
      )
      print 'Binding done!'
      return

   def keyboard_options(self, parent, variables, axis):
      radio = ttk.Radiobutton(parent, text = 'Keyboard/Button', variable = variables['input_type_radio'], value = 'keyboard')
      radio.grid(row = 1 , column = 1)
      keyboard_options_frame = ttk.LabelFrame(parent)
      keyboard_options_frame.grid(row = 2, column = 1, stick='N')

      # Create input binds
      for binding_number in range(3):
         option_frame = ttk.Frame(keyboard_options_frame)
         option_frame.grid(row = binding_number + 2, column = 1, columnspan = 5, stick='W', padx = 20)
         bound_button_widget = ttk.Label(option_frame, text = 'N/A')
         bound_button_widget.pack(side = 'left')
         # Create a button widget and bind it to bind_button_callback
         # This will configure the label and setup the hotkey
         entry_var = Tkinter.StringVar()
         variables['entry_%i' % binding_number] = entry_var
         button_widget = ttk.Button(
            option_frame,
            text = 'Bind',
            command = lambda var = entry_var, widget = bound_button_widget: self.bind_button_callback(widget, axis, var)
         ).pack(side = 'left')
         ttk.Label(option_frame, text = 'Value').pack(side = 'left')
         ttk.Entry(option_frame, width = 7, textvariable = entry_var).pack(side = 'left')

      # Create auto center options
      auto_center_frame = ttk.Frame(keyboard_options_frame)
      auto_center_frame.grid(row = 5, column = 1, columnspan = 5, stick='W', padx = 20)
      variables['auto_center'] = Tkinter.IntVar()
      entry = ttk.Entry(auto_center_frame, state = DISABLE, width = 5)
      checkbutton = ttk.Checkbutton(
         auto_center_frame,
         text = 'Auto center',
         variable = variables['auto_center']
      )

      def auto_center_changed_callback(*args):
         entry.state( ENABLE if variables['auto_center'].get() else DISABLE )
         return

      variables['auto_center'].trace('w', auto_center_changed_callback)
      
      checkbutton.pack(side = 'left')
      entry.pack(side = 'left')
      return keyboard_options_frame

   def joystick_options(self, parent, variables):
      radio = ttk.Radiobutton(parent, text = 'Joystick', variable = variables['input_type_radio'], value = 'joystick')
      radio.grid(row = 1 , column = 2)
      # Create the joystick options frame
      joystick_options_frame = ttk.LabelFrame(parent)
      joystick_options_frame.grid(row = 2, column = 2, stick='N')
      

      option_frame = ttk.Frame(joystick_options_frame)
      option_frame.grid(row = 2, column = 1, columnspan = 5, stick='W', padx = 20)
      # Joystick ID
      ttk.Label(option_frame, text = 'Joy ID').pack(side = 'left')
      # Get the list of joystick names
      joystick_names = ['']
      joystick_names.extend( ['%i - %s' % (joy.get_id()+1, joy.get_name()) for joy in self.joysticks.values()] )
      # Joystick ID widget
      joy_id_widget = ttk.Combobox(option_frame, width = 20, values = joystick_names, textvariable = variables['joystick_id'])
      joy_id_widget.pack(side = 'left')
      # Joystick Axis Widget
      joy_axis_widget = ttk.Combobox(option_frame, width = 5, state = DISABLE )
      joy_axis_widget.pack(side = 'left')

      # Changed axes selection based on joystick ID
      def joystick_id_changed_callback(*args):
         value = joy_id_widget.current()
         if value > 0:
            joy_axis_widget.state(ENABLE)
            joystick = self.joysticks[value - 1]
            joy_axis_widget.configure( values = range(1, joystick.get_numaxes() + 1) )
         else:
            joy_axis_widget.state(DISABLE)
         return
      variables['joystick_id'].trace('w', joystick_id_changed_callback)

      # Mapping methods
      ttk.Label(option_frame, text = 'TODO: Mapping Method').pack(side = 'left')

      return joystick_options_frame

   def mouse_options(self, parent, variables):
      radio = ttk.Radiobutton(parent, text = 'Mouse', variable = variables['input_type_radio'], value = 'mouse')
      radio.grid(row = 1 , column = 3)
      mouse_options_frame = ttk.LabelFrame(parent)
      mouse_options_frame.grid(row = 2, column = 3, stick='N')
      

      option_frame = ttk.Frame(mouse_options_frame)
      option_frame.grid(row = 2, column = 1, columnspan = 5, stick='W', padx = 20)

      ttk.Label(option_frame, text = 'Mouse Axis').pack(side = 'left')
      ttk.Combobox(option_frame, width = 5, values = ('', 'X', 'Y', 'Wheel')).pack(side = 'left')

      return mouse_options_frame
