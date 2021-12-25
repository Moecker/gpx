import os
import main
import graph
import pprint

pickle_path = os.path.join("pickle", "at" + "_" + str(1000) + "_" + "segments.p")
segments_dict = main.try_load_pickle(pickle_path)

print(len(segments_dict))

map = graph.Graph([])
print(map)

first = list(segments_dict.values())[0].points[0]
last = list(segments_dict.values())[-1].points[-1]

is_first_run = True
for _, segment in segments_dict.items():
    if len(segment.points):
        for point in segment.points[::] + [first] + [last]:
            if is_first_run:
                prev_point = point
                is_first_run = False
                continue
            map.add(prev_point, point)
            prev_point = point

print(map.nodes())
print(map.find_path(first, last))
