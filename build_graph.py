import os
import main
import graph
import gpx2ascii
import points2ascii
import distance
import config
from tqdm import tqdm
import pickle


def build_map_right(segments_dict):
    first = list(segments_dict.values())[0].points[0]
    last = list(segments_dict.values())[-1].points[-1]

    map = graph.Graph([])
    for _, segment in tqdm(segments_dict.items()):
        if len(segment.points):
            prev_point = None
            segment_points_iteratable = segment.points[:: config.PRECISION] + [first] + [last]
            for point in segment_points_iteratable:
                # Direct, inter segment connection
                if prev_point:
                    map.add(prev_point, point)
                prev_point = point

                for _, other_segment in segments_dict.items():
                    for other_point in other_segment.points[:: config.PRECISION]:
                        if point != other_point:
                            dis = distance.haversine_gpx(point, other_point)
                            if dis < 100:
                                map.add(point, other_point)
    return map


def build_map_wrong(segments_dict):
    first = list(segments_dict.values())[0].points[0]
    last = list(segments_dict.values())[-1].points[-1]

    map = graph.Graph([])
    is_first_run = True
    for _, segment in segments_dict.items():
        if len(segment.points):
            for point in segment.points + [first] + [last]:
                if is_first_run:
                    prev_point = point
                    is_first_run = False
                    continue
                map.add(prev_point, point)
                prev_point = point
    return map


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

    path_wrong = build_path(segments_dict, "map_wrong_at_1000.p", build_map_wrong)
    path_right = build_path(segments_dict,"map_right_at_1000.p", build_map_right)

    create_and_display_map(path_wrong)
    create_and_display_map(path_right)

    all_points = get_all_points(segments_dict)
    create_and_display_map(all_points)


def build_path(segments_dict, name, map_builder):
    map_right = load_pickle(segments_dict, name, map_builder)
    first = list(list(map_right._graph.values())[0])[0]
    last = list(list(map_right._graph.values())[-1])[-1]
    print(first)
    print(last)
    path_right = map_right.find_path(first, last)
    if not path_right:
        print("No path")
        return
    print(f"Length of path right: {len(path_right)}")
    return path_right


def get_all_points(segments_dict):
    all_points = []
    for _, segment in segments_dict.items():
        for point in segment.points:
            all_points.append(point)
    return all_points


def load_pickle(segments_dict, name, build_function):
    pickle_path = os.path.join("pickle", name)
    if not os.path.isfile(pickle_path):
        map_right = build_function(segments_dict)
        pickle.dump(map_right, open(pickle_path, "wb"))
    map_right = pickle.load(open(pickle_path, "rb"))
    return map_right


if __name__ == "__main__":
    run()
