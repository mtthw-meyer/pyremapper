#!/usr/bin/python
import uuid
import ctypes
import threading

import pythoncom
import pyHook


class KeyMouseManager:
   def __init__(self):
      self._keys_down = set()
      self._hotkeys = dict()
      self._key_sets = dict()

      # Create a hook manager
      self._hook_manager = pyHook.HookManager()

      # Setup listeners for key down and key up events
      self._hook_manager.KeyDown = self._on_key_down
      self._hook_manager.KeyUp = self._on_key_up

      # Set the keyboard hook
      self._hook_manager.HookKeyboard()
      
      self.add_hotkey(['Lcontrol','Lshift','Q'], self.end)
      
   def get_keys_down(self):
      return self._keys_down.copy()

   def _on_key_down(self, event):
      self._keys_down.add(ID2Key[event.KeyID])

      for hotkey in self._hotkeys.values():
         # Ignore on up hotkeys
         if hotkey.on_up:
            continue
         elif hotkey.match(self._keys_down):
            hotkey.run()
         elif self.hotkey_in_keyset(hotkey):
            hotkey.run()

      return True

   def _on_key_up(self, event):
      key_up = ID2Key[event.KeyID]
      key_up_set = frozenset(key_up)

      for hotkey in self._hotkeys.values():
         # Ignore on down hotkeys
         if not hotkey.on_up:
            continue
         # If its an up key 
         # AND it matches what was pushed
         # AND the key being released is a subset of the set, run the hotkey
         elif hotkey.match(self._keys_down) and key_up_set.issubset(hotkey._keys):
            hotkey.run()
         elif self.hotkey_in_keyset(hotkey) and not hotkey.issubset(self._keys_down - key_up_set):
            hotkey.run()
      self._keys_down.remove(key_up)

      return True
      
   def hotkey_in_keyset(self, hotkey):
      if hotkey.key_set is not None:
         if hotkey.issubset(self._keys_down):
            free_keys = self._keys_down
            for key in self._key_sets[hotkey.key_set]:
               free_keys = free_keys - key
            if len(free_keys) == 0:
               return True
      return False

   def add_hotkey(self, keys, func, on_up = False, **kwargs):
      id = uuid.uuid4().hex
      hotkey = HotKey(keys, func, on_up, **kwargs)
      self._hotkeys[id] = hotkey

      # 
      if hotkey.key_set is not None:
         # Check for existing key_set
         if hotkey.key_set not in self._key_sets:
            self._key_sets[hotkey.key_set] = set()
         self._key_sets[hotkey.key_set].add(hotkey._keys)

      return id

   def remove_hotkey(self, id):
      if id in self._hotkeys:
         self._hotkeys.pop(id)
         return True
      return False
   
   def pump(self):
      pythoncom.PumpWaitingMessages()
      return
      
   def end(self):
      ctypes.windll.user32.PostQuitMessage(0)


class HotKey:
   def __init__(self, keys, hotkey_func, on_up = False, key_set = None):
      self._keys = frozenset(keys)
      self.key_set = key_set
      self.hotkey_func = hotkey_func
      self.on_up = on_up
      
   def match(self, keys):
      return (self._keys == keys)
      
   def issubset(self, keys):
      return (self._keys.issubset(keys))

   def run(self):
      thread = threading.Thread(target = self.hotkey_func)
      thread.daemon = True
      thread.start()
      return
      
   def __repr__(self):
      return '%s' % self._keys


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
