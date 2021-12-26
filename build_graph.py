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


def build_map(segments_dict):
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


def add_waypoints(map, path, edges):
    for point in path:
        idx_w, idx_h = gpx2ascii.determine_index((point.latitude, point.longitude), edges)
        map[idx_w][idx_h] = "x"


def create_and_display_map(path, name):
    if not path:
        print("Nothing to display")
        return
    edges = points2ascii.determine_bounding_box(path)
    map = points2ascii.create_map(edges)
    add_waypoints(map, path, edges)
    print("Name: " + name)
    gpx2ascii.display(map)


def run():
    start = (46, 10)
    end = (48, 15)

    print("Loading segments")
    reduction = str(int(config.REDUCTION_DISTANCE))
    pickle_path_segments = os.path.join("pickle", "_".join([config.COUNTRY, reduction, "segments.p"]))
    segments_dict = main.try_load_pickle(pickle_path_segments)

    if not segments_dict:
        logging.error("Could not load segments")

    all_points = get_all_points(segments_dict)
    create_and_display_map(all_points, "All Points")

    connection = str(int(config.GRAPH_CONNECTION_DISTANCE))
    precision = str(int(config.PRECISION))
    map = load_or_build_map(
        segments_dict, "_".join([config.COUNTRY, "R" + reduction, "C" + connection, "P" + precision, "map.p"])
    )

    print("Finding random paths")
    random_path = find_path(map, start, end, map.find_path)
    create_and_display_map(random_path, "Random Path")

    print("Finding shortest path")
    shortest = find_path(map, start, end, map.find_shortest_path)
    create_and_display_map(shortest, "Shortest Path")

    if False:
        print("Finding multipath")
        all_paths = find_path(map, start, end, map.find_all_paths)
        for i, path in enumerate(all_paths):
            print(f"Length of path: {len(path)}")
            create_and_display_map(path, str(i) + ". Path ")


def compute_min_dis(map, start_gpx):
    min_dis = math.inf
    min_node = None
    for k, v in map._graph.items():
        dis = distance.haversine_gpx(k, start_gpx)
        if dis < min_dis:
            min_dis = dis
            min_node = k
    return min_dis, min_node


def get_closest_start_and_end(map, start, end):
    print("Number of nodes in graph " + str(len(map._graph.values())))

    start_gpx = gpxpy.gpx.GPXTrackPoint(start[0], start[1])
    end_gpx = gpxpy.gpx.GPXTrackPoint(end[0], end[1])

    print("Desired start: " + str(start_gpx))
    print("Desired end: " + str(end_gpx))

    min_dis_start, first = compute_min_dis(map, start_gpx)
    min_dis_end, last = compute_min_dis(map, end_gpx)

    print("Min distance start: " + str(min_dis_start))
    print("Min distance end: " + str(min_dis_end))

    print("Min node start: " + str(first))
    print("Min node end: " + str(last))
    return first, last


def find_path(map, start, end, strategy):
    first, last = get_closest_start_and_end(map, start, end)

    path = strategy(first, last)
    if not path:
        print("No path found")
        return

    print(f"Length of path(s): {len(path)}")
    return path


def get_all_points(segments_dict):
    all_points = []
    for _, segment in segments_dict.items():
        for point in segment.points:
            all_points.append(point)
    return all_points


def load_or_build_map(segments_dict, name):
    pickle_path = os.path.join("pickle", name)
    if not os.path.isfile(pickle_path):
        print("Pickle " + pickle_path + " does not exist")
        map = build_map(segments_dict)
        pickle.dump(map, open(pickle_path, "wb"))
    print("Loading " + pickle_path)
    map = pickle.load(open(pickle_path, "rb"))
    return map


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
