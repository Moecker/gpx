import os
import main
import graph
import pprint
import gpx2ascii
import points2ascii
import distance


def build_map(segments_dict, first, last):
    map = graph.Graph([])
    all_points = []
    is_first_run = True
    for _, segment in segments_dict.items():
        if len(segment.points):
            for point in segment.points + [first] + [last]:
                all_points.append(point)
                if is_first_run:
                    prev_point = point
                    is_first_run = False
                    continue
                map.add(prev_point, point)
                prev_point = point
    return map, all_points


def add_waypoints(map, path, edges):
    for point in path:
        idx_w, idx_h = gpx2ascii.determine_index((point.latitude, point.longitude), edges)
        map[idx_w][idx_h] = "x"


def create_and_display_map(path):
    edges = points2ascii.determine_bounding_box(path)
    map = points2ascii.create_map(edges)
    add_waypoints(map, path, edges)
    gpx2ascii.display(map)


def run():
    pickle_path = os.path.join("pickle", "at" + "_" + str(1000) + "_" + "segments.p")
    segments_dict = main.try_load_pickle(pickle_path)

    first = list(segments_dict.values())[0].points[0]
    last = list(segments_dict.values())[-1].points[-1]

    map, all_points = build_map(segments_dict, first, last)

    path = map.find_path(first, last)
    print(f"Length of path: {len(path)}")

    create_and_display_map(path)
    create_and_display_map(all_points)


if __name__ == "__main__":
    run()
