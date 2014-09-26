import tkFileDialog
import pickle


class MappingManager(object):
   def __init__(self, keymouse_manager, joystick_manager):
      self.joystick_manager = joystick_manager
      self.keymouse_manager = keymouse_manager
      return

   def load(self, filename = None):
      if filename is None:
         filename = tkFileDialog.askopenfilename()
         if filename is '':
            return

      f = open(filename, 'rb')
      data = pickle.load(f)
      print data
      self.keymouse_manager.hotkeys = data.get(('keymouse_manager_hotkeys'), dict())
      self.keymouse_manager.key_sets = data.get(('keymouse_manager_key_sets'), dict())
      self.joystick_manager.mappings = data.get(('joystick_manager_mappings'), dict())
      f.close()
      return

   def save(self, filename = None):
      if filename is None:
         filename = tkFileDialog.asksaveasfilename()
         if filename is '':
            return

      f = open(filename, 'wb')
      data = {
         ('keymouse_manager_hotkeys'): self.keymouse_manager.hotkeys,
         ('keymouse_manager_key_sets'): self.keymouse_manager.key_sets,
         ('joystick_manager_mappings'): self.joystick_manager.mappings,
      }
      print data
      pickle.dump(data, f, -1)
      f.close()
      return
