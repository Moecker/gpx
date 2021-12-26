import math
import gpxpy.gpx
import os
import main
import graph
import gpx2ascii
import points2ascii
import distance
import config
from tqdm import tqdm
import pickle
import logging
import sys

sys.setrecursionlimit(2000)


def build_map_right(segments_dict):
    map = graph.Graph([])
    for _, segment in tqdm(segments_dict.items()):
        if len(segment.points):
            prev_point = None
            segment_points_iteratable = segment.points[:: config.PRECISION]
            for point in segment_points_iteratable:
                # Direct, inter segment connection
                if prev_point:
                    map.add(prev_point, point)
                prev_point = point

                for _, other_segment in segments_dict.items():
                    for other_point in other_segment.points[:: config.PRECISION]:
                        if point != other_point:
                            dis = distance.haversine_gpx(point, other_point)
                            if dis < config.GRAPH_CONNECTION_DISTANCE:  # in km
                                map.add(point, other_point)
    return map


def build_map_wrong(segments_dict):
    map = graph.Graph([])
    is_first_run = True
    for _, segment in segments_dict.items():
        if len(segment.points):
            for point in segment.points:
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


def create_and_display_map(path, name):
    if not path:
        print("Nothing to display, skipping")
        return
    edges = points2ascii.determine_bounding_box(path)
    map = points2ascii.create_map(edges)
    add_waypoints(map, path, edges)
    print(name)
    gpx2ascii.display(map)


def explore_multi_path(map_right, start, end):
    first, last = get_closest_start_and_end(map_right, start, end)
    paths = map_right.find_all_paths(first, last)
    print("Length of multipath: " + str(len(paths)))

    shortest = map_right.find_shortest_path(first, last)
    print("Length of shortest: " + str(len(shortest)))
    return paths, shortest


def run():
    start = (46, 10)
    end = (48, 15)

    print("Loading segments")
    red_distance_string = str(int(config.REDUCTION_DISTANCE))
    pickle_path = os.path.join("pickle", "at" + "_" + red_distance_string + "_" + "segments.p")
    segments_dict = main.try_load_pickle(pickle_path)

    all_points = get_all_points(segments_dict)
    create_and_display_map(all_points, "All Points")

    print("Building paths")

    map_right, path_right = build_path(
        segments_dict, "map_right_at_" + red_distance_string + ".p", build_map_right, start, end
    )
    create_and_display_map(path_right, "Right Path")

    paths, shortest = explore_multi_path(map_right, start, end)
    create_and_display_map(shortest, "Shortest")

    for i, path in enumerate(paths):
        create_and_display_map(path, "Path " + str(i))


def compute_min_dis(map_right, start_gpx):
    min_dis = math.inf
    min_node = None
    for k, v in map_right._graph.items():
        dis = distance.haversine_gpx(k, start_gpx)
        if dis < min_dis:
            min_dis = dis
            min_node = k
    return min_dis, min_node


def get_closest_start_and_end(map_right, start, end):
    print("Number of nodes in graph " + str(len(map_right._graph.values())))

    start_gpx = gpxpy.gpx.GPXTrackPoint(start[0], start[1])
    end_gpx = gpxpy.gpx.GPXTrackPoint(end[0], end[1])

    print("Desired start: " + str(start_gpx))
    print("Desired end: " + str(end_gpx))

    min_dis_start, first = compute_min_dis(map_right, start_gpx)
    min_dis_end, last = compute_min_dis(map_right, end_gpx)

    print("Min distance start: " + str(min_dis_start))
    print("Min distance end: " + str(min_dis_end))

    print("Min node start: " + str(first))
    print("Min node end: " + str(last))
    return first, last


def build_path(segments_dict, name, map_builder, start, end):
    map_right = load_pickle(segments_dict, name, map_builder)

    first, last = get_closest_start_and_end(map_right, start, end)
    print("Finding path")
    path_right = map_right.find_path(first, last)
    if not path_right:
        print("No path found")
        return
    print(f"Length of path: {len(path_right)}")
    return map_right, path_right


def get_all_points(segments_dict):
    all_points = []
    for _, segment in segments_dict.items():
        for point in segment.points:
            all_points.append(point)
    return all_points


def load_pickle(segments_dict, name, build_function):
    pickle_path = os.path.join("pickle", name)
    if not os.path.isfile(pickle_path):
        print("Pickle " + pickle_path + " does not exist")
        map_right = build_function(segments_dict)
        pickle.dump(map_right, open(pickle_path, "wb"))
    print("Loading " + pickle_path)
    map_right = pickle.load(open(pickle_path, "rb"))
    return map_right


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
