import cPickle


class MappingManager(object):
   INI_FILE = 'pyremapper.ini'
   FIELDS = ('type')

   def __init__(self, joystick_manager, keymouse_manager, functions = None):
      self.joystick_manager = joystick_manager
      self.keymouse_manager = keymouse_manager
      return

   def load(self, file_name):
      f = open(file_name, 'rb')
      data = cPickle.load(f)
      self.keymouse_manager.hotkeys = data.get(('keyboard_manager', 'hotkeys'), dict())
      self.keymouse_manager.key_sets = data.get(('keyboard_manager', 'key_sets'), dict())
      self.joystick_manage.mappings = data.get(('joystick_manager', 'mappings'), dict())
      f.close()
      return

   def save(self, file_name):
      f = open(file_name, 'wb')
      data = {
         ('keyboard_manager', 'hotkeys'): self.keymouse_manager.hotkeys,
         ('keyboard_manager', 'key_sets'): self.keymouse_manager.key_sets,
         ('joystick_manager', 'mappings'): self.joystick_manage.mappings,
      }
      cPickle.dump(data, f, -1)
      f.close()
      return
