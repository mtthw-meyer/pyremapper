import sys
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
      'name':     'Example-Linear',
      'function': linear,
   },
   {
      'name':     'Example-Invert',
      'function': invert,
   },
]


if __name__ == '__main__':
   log_file = open('remapper.log', 'w')
   sys.stdout = log_file
   sys.stderr = log_file
   remapper = Remapper(mapping_functions = mapping_functions)
   remapper.start()
   log_file.close()
