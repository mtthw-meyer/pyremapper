import sys
from pyremapper.remapper import Remapper


# The input value is from 1 to -1, with 0 being centered
# Out of bounds values will be rouned to the nearest valid value
def logarithmic(value):
   import math
   # Log base 10 of 10 is 1 so input values to log should be between 1-10
   in_range_value = (abs(value) + 1) * 10
   if value < 0:
      return math.log(in_range_value, 10) * -1
   else:
      return math.log(in_range_value, 10)


def squared(value):
   # If less than 5% deflection ignore it
   if abs(value) < 0.05:
      return 0
   # Any where in the last 5% deflection should be treated as 100%
   if abs(value) >= .95:
      return round(value)
   # else reutrn the square
   # 10% is 1% deflection
   # 20% is 4% deflection
   # 30% is 9% deflection
   # 40% is 16% deflection
   # 50% is 25% deflection
   return (value * value)


mapping_functions = [
   {
      'name':     'Logarithmic',
      'function': logarithmic,
   },
   {
      'name':     'Squared Deadzone',
      'function': squared,
   },
]


if __name__ == '__main__':
   log_file = open('remapper.log', 'w')
   #sys.stdout = log_file
   #sys.stderr = log_file
   remapper = Remapper(mapping_functions = mapping_functions)
   remapper.start()
   log_file.close()
