


import time
import matplotlib.pyplot as plt
from rich.progress import track

list_x = []
for k in range(10, 10000, 10):
    list_x.append(k)

list_Y1 = []
list_Y2 = []
list_Y3 = []
for max_key in track(list_x, description="Testing"):
    print(f"Testing with max key: {max_key}")
    tries = 1000000
    # We will find the key in the middle of the map
    key_to_find = (max_key // 2)
    
    # Setup
    map = {}
    for i in range(max_key):
        map[i] = i

    # Test 1: if key_to_find in map
    values = []
    for k in range(tries):
        start = time.time()
        if key_to_find in map:
            pass
        elapsed = time.time() - start
        values.append(elapsed)
        # print(f"Found {i} in {elapsed} seconds")
    # print(f"Average time for 'if key_to_find in map' operation: {sum(values) / len(values)} seconds")
    list_Y1.append(sum(values) / len(values))

    # Test 2: try: map[key_to_find] except KeyError: pass
    values = []
    for k in range(tries):
        start = time.time()
        try:
            map[key_to_find]
        except KeyError:
            pass
        elapsed = time.time() - start
        values.append(elapsed)
        # print(f"Found {i} in {elapsed} seconds")
    # print(f"Average time for 'try: map[key_to_find] except KeyError: pass' operation: {sum(values) / len(values)} seconds")
    list_Y2.append(sum(values) / len(values))

    # Test 3: if key_to_find in map.keys()
    values = []
    for k in range(tries):
        start = time.time()
        if key_to_find in map.keys():
            pass
        elapsed = time.time() - start
        values.append(elapsed)
        # print(f"Found {i} in {elapsed} seconds")
    # print(f"Average time for 'if key_to_find in map.keys()' operation: {sum(values) / len(values)} seconds")
    list_Y3.append(sum(values) / len(values))

# Plot the results
plt.plot(list_x, list_Y1, label='if key_to_find in map')
plt.plot(list_x, list_Y2, label='try: map[key_to_find] except KeyError: pass')
plt.plot(list_x, list_Y3, label='if key_to_find in map.keys()')

plt.xlabel('Number of keys in map')
plt.ylabel('Time (seconds)')
plt.legend()
plt.title('Time taken to find key in map')
plt.show()