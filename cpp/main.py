import time
import fibinacci as pbe

def fibinacci_py(x):
    if x < 2:
        return x
    return fibinacci_py(x - 1) + fibinacci_py(x - 2)

n = 40

print('Python:')
start_time = time.perf_counter_ns()
print('Answer:', fibinacci_py(n))
print('Time:', (time.perf_counter_ns() - start_time) / 1e9, 's')
print()

print('C++:')
start_time = time.perf_counter_ns()
print('Answer:', pbe.fibinacci_cpp(n))
print('Time:', (time.perf_counter_ns() - start_time) / 1e9, 's')
