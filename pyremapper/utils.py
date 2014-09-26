import Tkinter

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
