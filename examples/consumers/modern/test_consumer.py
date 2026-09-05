import os
import sys
sys.path.insert(0, os.environ['RADAR_PACKAGE'])
from tinycalc import add
assert add(2, 3) == 5
print('numeric inputs still work')
