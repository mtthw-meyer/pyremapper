
class Enum(object):
   def __init__(self, items):
      self.__items = items
      self.__length = len(items)
      self.__range = range(self.__length)
      for item, value in zip(self.__items, self.__range):
         setattr(self, item, value)
      return

   def __len__(self):
      return self.__length

   def __iter__(self):
      return self.__range.__iter__()
