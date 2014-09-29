import traceback
from functools import wraps

from dialog import ExceptionDialog



DISABLE = ('disabled',)
ENABLE = ('!disabled',)

def set_state_recursive(widget, state):
   try:
      widget.state(state)
   except:
      pass
   for child in widget.winfo_children():
      set_state_recursive(child, state)
   return


def exception_handler(function):
   @wraps(function)
   def wrapper(self, *args, **kwargs):
      try:
         return function(self, *args, **kwargs)
      except Exception, e:
         error = 'Error: %s' % (e)
         ExceptionDialog(self.parent, traceback.format_exc())
      return
   return wrapper
