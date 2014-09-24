import Tkinter
import ttk

import time
import threading
import Queue


class Dialog(Tkinter.Toplevel):
   def __init__(self, parent, title = None):
      Tkinter.Toplevel.__init__(self, parent)
      self.transient(parent)
      self.parent = parent
      self.result = None
      self.done = False

      if title is not None:
         self.title(title)

      # Bindings
      self.bind('<Return>', self.ok)
      self.bind('<Escape>', self.cancel)

      # Body
      body = ttk.Frame(self)
      self.initial_focus = self.body(body)
      body.pack(padx=5, pady=5)
      self.buttonbox()
      self.grab_set()

      if not self.initial_focus:
         self.initial_focus = self

      self.protocol('WM_DELETE_WINDOW', self.cancel)
      self.geometry("+%d+%d" % (parent.winfo_rootx()+250, parent.winfo_rooty()+250))
      self.initial_focus.focus_set()
      self.initialize()
      self.wait_window(self)

   def initialize(self):
      pass

   def body(self, parent):
      # create dialog body.  return widget that should have
      # initial focus.  this method should be overridden
      pass

   def buttonbox(self):
      # add standard button box. override if you don't want the
      # standard buttons
      box = ttk.Frame(self)

      #w = ttk.Button(box, text="OK", width=10, command=self.ok, default=Tkinter.ACTIVE)
      #w.pack(side='left', padx=5, pady=5)
      w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
      w.pack(side='left', padx=5, pady=5)

      box.pack()
      return

   def ok(self, event=None):
      if not self.validate():
         self.initial_focus.focus_set() # put focus back
         return
      self.withdraw()
      self.update_idletasks()
      self.apply()
      self.cancel()
      return

   def cancel(self, event=None):
      # put focus back to the parent window
      self.done = True
      self.parent.focus_set()
      self.destroy()
      return

   def validate(self):
      return 1

   def apply(self):
      pass


class Binder(Dialog):
   MODIFIERS = frozenset(['Lshift', 'Rshift', 'Lcontrol', 'Rcontrol', 'Lmenu', 'Rmenu', 'Lwin', 'Rwin'])

   def __init__(self, parent, keyboard_manager, title = None):
      self.keyboard_manager = keyboard_manager
      self.thread = None
      self.queue = Queue.Queue()
      Dialog.__init__(self, parent, title)
      return

   def initialize(self):
      self.bind('<<Bound>>', self.ok)
      self.after(50, self.wait_for_keys)
      # Start key listener
      self.thread = threading.Thread(target = self.key_listener)
      self.thread.start()
      return
      
   def buttonbox(self):
      pass

   def wait_for_keys(self):
      try:
         self.value = self.queue.get(block = False)
      except Queue.Empty:
         self.after(50, self.wait_for_keys)
      else:
         self.ok()
      return

   def key_listener(self):
      while not self.done and not (self.keyboard_manager.get_keys_down() - self.MODIFIERS):
         time.sleep(.05)
      if not self.done:
         self.queue.put( self.keyboard_manager.get_keys_down() )
      return
   