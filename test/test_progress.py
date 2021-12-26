from tqdm import tqdm
import time

n = 5
m = 300

with tqdm(total=n * m) as pbar:
    for i1 in tqdm(range(n)):
        for i2 in tqdm(range(m)):
            time.sleep(0.01)
            pbar.update(1)
