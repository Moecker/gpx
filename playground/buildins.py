import numpy as np
import sys


def print_size_of(thing):
    print(sys.getsizeof(thing))


print_size_of(np.float16(1))
print_size_of(np.float16(1.0))
print_size_of(1.0)
print_size_of(np.int64(1))
