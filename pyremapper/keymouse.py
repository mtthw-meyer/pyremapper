import uuid
import ctypes
import threading

import pyHook




class KeyMouseManager(object):
   def __init__(self, joystick_manager):
      self.joystick_manager = joystick_manager
      self.keys_down = set()
      self.hotkeys = dict()
      self.keysets = dict()
      self.mappings = dict()

      # Create a hook manager
      self.hook_manager = pyHook.HookManager()

      # Setup listeners for key down and key up events
      self.hook_manager.KeyDown = self.on_key_down
      self.hook_manager.KeyUp = self.on_key_up
      self.hook_manager.MouseAllButtonsDown = self.on_key_down
      self.hook_manager.MouseAllButtonsUp = self.on_key_up

      # Set the hooks
      self.hook_manager.HookKeyboard()
      self.hook_manager.HookMouse()
      return

   def get_keys_down(self):
      return self.keys_down.copy()

   def on_mouse_event(self, event):
      # Ignoring mouse events
      return True

   def on_key_down(self, event):
      # Ignoring mouse events
      if event.MessageName.startswith('mouse'):
         # Trim ' down' from the end of the event name
         self.keys_down.add(event.MessageName[:-5])
      else:
         self.keys_down.add(ID2Key[event.KeyID])
      for hotkey_dict in self.hotkeys.values():
         for hotkey in hotkey_dict.values():
            # Ignore on up hotkeys
            if hotkey.on_up:
               continue
            elif hotkey.match(self.keys_down):
               args = hotkey.vjoy_tuple + (hotkey.value,)
               self.joystick_manager.set_component_value(*args)
            elif self.hotkey_inkeyset(hotkey):
               args = hotkey.vjoy_tuple + (hotkey.value,)
               self.joystick_manager.set_component_value(*args)

      return True

   def on_key_up(self, event):
      # Ignoring mouse events
      if event.MessageName.startswith('mouse'):
         # Trim ' up' from the end of the event name
         key_up = event.MessageName[:-3]
         key_up_set = frozenset([key_up])
      else:
         key_up = ID2Key[event.KeyID]
         key_up_set = frozenset(key_up)
      print key_up_set, self.keys_down

      for hotkey_dict in self.hotkeys.values():
         for hotkey in hotkey_dict.values():
            # Ignore on down hotkeys
            if not hotkey.on_up:
               continue
            # If its an up key 
            # AND it matches what was pushed
            # AND the key being released is a subset of the set, run the hotkey
            elif hotkey.match(self.keys_down) and key_up_set.issubset(hotkey.keys):
               args = hotkey.vjoy_tuple + (hotkey.value,)
               self.joystick_manager.set_component_value(*args)
            elif self.hotkey_inkeyset(hotkey) and not hotkey.issubset(self.keys_down - key_up_set):
               args = hotkey.vjoy_tuple + (hotkey.value,)
               self.joystick_manager.set_component_value(*args)

      if key_up in self.keys_down:
         self.keys_down.remove(key_up)
      return True
      
   def hotkey_inkeyset(self, hotkey):
      if hotkey.keyset is not None:
         if hotkey.issubset(self.keys_down):
            freekeys = self.keys_down
            for key in self.keysets[hotkey.keyset]:
               freekeys = freekeys - key
            if len(freekeys) == 0:
               return True
      return False

   def add_hotkey(self, keys, value, vjoy_tuple, binding, on_up = False, keyset = None):
      hotkey_dict = self.hotkeys.setdefault(vjoy_tuple, dict())
      if binding in hotkey_dict:
         self.update_hotkey(vjoy_tuple, binding, value = value)
      else:
         hotkey = Hotkey(keys, value, vjoy_tuple, on_up, keyset)
         hotkey_dict[binding] = hotkey
         if keyset is not None:
            self.keysets.setdefault(keyset, set()).add(hotkey.keys)

      return vjoy_tuple

   def update_hotkey(self, vjoy_tuple, binding, keys = None, value = None, keyset = None):
      hotkey_dict = self.hotkeys.get(vjoy_tuple, None)
      if hotkey_dict is None:
         return False

      hotkey = hotkey_dict.get(binding)
      if hotkey is None:
         return False

      if keys is not None:
         hotkey.keys = keys
      if value is not None:
         hotkey.value = value
      if keyset is not None:
         hotkey.keyset = keyset
         self.keysets.setdefault(keyset, set()).add(hotkey.keys)

      return True
      
   def update_hotkeys(self, vjoy_tuple, keys = None, value = None, keyset = None):
      hotkey_dict = self.hotkeys.get(vjoy_tuple, None)
      if hotkey_dict is None:
         return False

      for binding, hotkey in hotkey_dict.items():
         self.update_hotkey(vjoy_tuple, binding, keys, value, keyset)
      return True

   def remove_hotkey(self, vjoy_tuple, binding):
      if vjoy_tuple in self.hotkeys:
         if binding in self.hotkeys[vjoy_tuple]:
            return self.hotkeys[vjoy_tuple].pop(binding)
      return

   def remove_hotkeys(self, vjoy_tuple):
      if vjoy_tuple in self.hotkeys:
         return self.hotkeys.pop(vjoy_tuple)
      return

   def quit(self):
      ctypes.windll.user32.PostQuitMessage(0)


class Hotkey(object):
   def __init__(self, keys, value, vjoy_tuple, on_up, keyset):
      self.keys = frozenset(keys)
      self.vjoy_tuple = vjoy_tuple
      self.value = value
      self.on_up = on_up
      self.keyset = keyset
      return

   def match(self, keys):
      return (self.keys == keys)

   def issubset(self, keys):
      return (self.keys.issubset(keys))


ID2Key = {
   8: 'Back',
   9: 'Tab',
   13: 'Return',
   20: 'Capital',
   27: 'Escape',
   32: 'Space',
   33: 'Prior',
   34: 'Next',
   35: 'End',
   36: 'Home',
   37: 'Left',
   38: 'Up',
   39: 'Right',
   40: 'Down',
   44: 'Snapshot',
   46: 'Delete',
   48: '0',
   49: '1',
   50: '2',
   51: '3',
   52: '4',
   53: '5',
   54: '6',
   55: '7',
   56: '8',
   57: '9',
   65: 'A',
   66: 'B',
   67: 'C',
   68: 'D',
   69: 'E',
   70: 'F',
   71: 'G',
   72: 'H',
   73: 'I',
   74: 'J',
   75: 'K',
   76: 'L',
   77: 'M',
   78: 'N',
   79: 'O',
   80: 'P',
   81: 'Q',
   82: 'R',
   83: 'S',
   84: 'T',
   85: 'U',
   86: 'V',
   87: 'W',
   88: 'X',
   89: 'Y',
   90: 'Z',
   91: 'Lwin',
   96: 'Numpad0',
   97: 'Numpad1',
   98: 'Numpad2',
   99: 'Numpad3',
   100: 'Numpad4',
   101: 'Numpad5',
   102: 'Numpad6',
   103: 'Numpad7',
   104: 'Numpad8',
   105: 'Numpad9',
   106: 'Multiply',
   107: 'Add',
   109: 'Subtract',
   110: 'Decimal',
   111: 'Divide',
   112: 'F1',
   113: 'F2',
   114: 'F3',
   115: 'F4',
   116: 'F5',
   117: 'F6',
   118: 'F7',
   119: 'F8',
   120: 'F9',
   121: 'F10',
   122: 'F11',
   123: 'F12',
   144: 'Numlock',
   160: 'Lshift',
   161: 'Rshift',
   162: 'Lcontrol',
   163: 'Rcontrol',
   164: 'Lmenu',
   165: 'Rmenu',
   186: 'Oem_1',
   187: 'Oem_Plus',
   188: 'Oem_Comma',
   189: 'Oem_Minus',
   190: 'Oem_Period',
   191: 'Oem_2',
   192: 'Oem_3',
   219: 'Oem_4',
   220: 'Oem_5',
   221: 'Oem_6',
   222: 'Oem_7',
   1001: 'mouse left', #mouse hotkeys
   1002: 'mouse right',
   1003: 'mouse middle',
   1000: 'mouse move', #single event hotkeys
   1004: 'mouse wheel up',
   1005: 'mouse wheel down',
   1010: 'Ctrl', #merged hotkeys
   1011: 'Alt',
   1012: 'Shift'
}

if __name__ == '__main__':
   key_mouse_manager = KeyMouseManager()
