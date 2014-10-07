import sys
from pyremapper.remapper import Remapper


# The input value is from 1 to -1, with 0 being centered
# Out of bounds values will be rouned to the nearest valid value
def logarithmic(value):
   import math
   # Log base 10 of 10 is 1 so input values to log should be between 1-10
   in_range_value = (abs(value) * 10) + 1
   if value < 0:
      return math.log(in_range_value, 10) * -1
   else:
      return math.log(in_range_value, 10)


def sigmoid(value):
      return (1.25 * value) / (1 + abs(value))


mapping_functions = [
   {
      'name':     'Logarithmic',
      'function': logarithmic,
   },
   {
      'name':     'Sigmoid',
      'function': sigmoid,
   },
]


if __name__ == '__main__':
   log_file = open('remapper.log', 'w')
   #sys.stdout = log_file
   #sys.stderr = log_file
   remapper = Remapper(mapping_functions = mapping_functions)
   remapper.start()
   log_file.close()
