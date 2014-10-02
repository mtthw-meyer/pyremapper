import Tkinter
import ttk


class ScrollingNotebook(ttk.Notebook):
   def __init__(self, parent):
      self.frame = ttk.Frame(parent)
      self.frame.grid_rowconfigure(0, weight=1)
      self.frame.grid_columnconfigure(0, weight=1)

      # Create canvas parent to contain the scrollbars
      self.canvas = Tkinter.Canvas(self.frame)
      self.canvas.grid(row = 0, column = 0, sticky='nsew')
      self.canvas.configure( highlightthickness = 0 )
      ttk.Notebook.__init__(self, self.canvas)

      # These scrollbars are made for scrollin'
      vertical_scrollbar = AutoScrollbar(self.frame, orient = 'vertical', command = self.canvas.yview)
      vertical_scrollbar.grid(row = 0, column = 1, sticky = 'ns')
      horizontal_scrollbar = AutoScrollbar(self.frame, orient = 'horizontal', command = self.canvas.xview)
      horizontal_scrollbar.grid(row = 1, column = 0, sticky = 'we' )

      self.canvas.configure( xscrollcommand = horizontal_scrollbar.set, yscrollcommand = vertical_scrollbar.set )
      self.canvas.create_window(0, 0, window = self, anchor = 'nw')
      return

   # Override the default add to configure the scrollable area when a tab is added
   def add(self, *args, **kwargs):
      result = ttk.Notebook.add(self, *args, **kwargs)
      self.update_idletasks()
      self.canvas.configure( scrollregion = (0, 0, self.winfo_width(), self.winfo_height()) )
      return result

   # Override pack/grid to effect the base frame
   def pack(self, *args, **kwargs):
      return self.frame.pack(*args, **kwargs)

   def grid(self, *args, **kwargs):
      return self.frame.grid(*args, **kwargs)


# Originally from
# http://effbot.org/zone/tkinter-autoscrollbar.htm      
class AutoScrollbar(ttk.Scrollbar):
   # a scrollbar that hides itself if it's not needed.  only
   # works if you use the grid geometry manager.
   def set(self, lo, hi):
      if float(lo) <= 0.0 and float(hi) >= 1.0:
         # grid_remove is currently missing from Tkinter!
         self.tk.call("grid", "remove", self)
      else:
         self.grid()
      ttk.Scrollbar.set(self, lo, hi)
      return

   def pack(self, **kw):
      raise TclError, "cannot use pack with this widget"

   def place(self, **kw):
      raise TclError, "cannot use place with this widget"
