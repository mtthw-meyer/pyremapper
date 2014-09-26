from pyremapper.remapper import Remapper


# The input value is from 1 to -1, with 0 being centered
# Out of bounds values will be rouned to the nearest valid value
def linear(value):
   return value


def invert(value):
   value = value * -1
   return value

mapping_functions = [
   {
      'name':     'Linear',
      'function': linear,
   },
   {
      'name':     'Invert',
      'function': invert,
   },
]


if __name__ == '__main__':
   remapper = Remapper(mapping_functions = mapping_functions)
   remapper.start()