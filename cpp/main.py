import time
import fibonacci as pbe


def fibonacci_py(x):
    if x < 2:
        return x
    return fibonacci_py(x - 1) + fibonacci_py(x - 2)


n = 35

print("C++:")
start_time = time.perf_counter_ns()
print("Answer:", pbe.fibonacci(n))
print("Time:", (time.perf_counter_ns() - start_time) / 1e9, "s")

print("Python:")
start_time = time.perf_counter_ns()
print("Answer:", fibonacci_py(n))
print("Time:", (time.perf_counter_ns() - start_time) / 1e9, "s")
