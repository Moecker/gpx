import logging
import math
import os
import pickle

import gpxpy.gpx
from tqdm import tqdm

import build_segments
import config
import distance
import gpx2ascii
import graph
import points2ascii


def build_map(segments_dict):
    map = graph.Graph([])
    for _, segment in tqdm(segments_dict.items()):
        if len(segment.points):
            prev_point = None
            segment_points_iteratable = segment.points[:: config.PRECISION]
            for point in segment_points_iteratable:
                # Direct, inter segment connection is always possible, without checking the distance
                if prev_point:
                    map.add(prev_point, point)
                prev_point = point
                update_segments_dict(segments_dict, map, point)
    return map


def update_segments_dict(segments_dict, map, point):
    for _, other_segment in segments_dict.items():
        for other_point in other_segment.points[:: config.PRECISION]:
            if point != other_point:
                dis = distance.haversine_gpx(point, other_point)
                if dis < config.GRAPH_CONNECTION_DISTANCE:
                    map.add(point, other_point)


def add_waypoints(map, path, edges, character):
    for point in path:
        idx_w, idx_h = gpx2ascii.determine_index((point.latitude, point.longitude), edges)
        map[idx_w][idx_h] = character


def create_and_display_map(path, name, background=[]):
    if not path:
        logging.warning("Nothing to display")
        return

    edges = points2ascii.determine_bounding_box(path + background)
    map = points2ascii.create_map(edges, " ")

    add_waypoints(map, background, edges, ".")
    add_waypoints(map, path, edges, "x")

    logging.info(f"Displaying map name: {name}")
    gpx2ascii.display(map)


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
    start_gpx = gpxpy.gpx.GPXTrackPoint(start[0], start[1])
    end_gpx = gpxpy.gpx.GPXTrackPoint(end[0], end[1])

    logging.info(f"Desired start GPS: {str(start_gpx)}")
    logging.info(f"Desired end GPS: {str(end_gpx)}")

    min_dis_start, first = compute_min_dis(map, start_gpx)
    min_dis_end, last = compute_min_dis(map, end_gpx)

    logging.info(f"Min distance start: {str(min_dis_start)}")
    logging.info(f"Min distance end: {str(min_dis_end)}")

    logging.info(f"Min node start GPS: {str(first)}")
    logging.info(f"Min node end GPS: {str(last)}")
    return first, last


def find_path(map, start, end, strategy):
    first, last = get_closest_start_and_end(map, start, end)

    path = strategy(first, last)
    if not path:
        logging.error(f"No path found from {first} to {last}")
        return None

    logging.info(f"Path(s) found, length of path(s): {len(path)}")
    return path


def collect_all_points(segments_dict):
    all_points = []
    for _, segment in segments_dict.items():
        for point in segment.points:
            all_points.append(point)
    return all_points


def load_or_build_map(segments_dict, name, output_dir):
    pickle_path = os.path.join(output_dir, name)
    if config.ALWAYS_GRAPH or not os.path.isfile(pickle_path):
        logging.info(f"Pickle {pickle_path} does not exist, creating map")
        map = build_map(segments_dict)

        logging.info(f"Saving pickle file to {pickle_path}")
        pickle.dump(map, open(pickle_path, "wb"))

    logging.info(f"Loading {pickle_path}")
    map = pickle.load(open(pickle_path, "rb"))

    return map


def standalone_example():
    start = (46, 10)
    end = (48, 15)

    print("Loading segments")
    reduction = str(int(config.REDUCTION_DISTANCE))
    pickle_path_segments = os.path.join("pickle", "_".join([config.COUNTRY, reduction, "segments.p"]))
    segments_dict = build_segments.try_load_pickle(pickle_path_segments)

    if not segments_dict:
        logging.error("Could not load segments")

    all_points = collect_all_points(segments_dict)
    create_and_display_map(all_points, "All Points")

    connection = str(int(config.GRAPH_CONNECTION_DISTANCE))
    precision = str(int(config.PRECISION))
    map = load_or_build_map(
        segments_dict, "_".join([config.COUNTRY, "R" + reduction, "C" + connection, "P" + precision, "map.p"]), "pickle"
    )

    print("Finding random paths")
    random_path = find_path(map, start, end, map.find_path)
    create_and_display_map(random_path, "Random Path")

    print("Finding shortest path")
    shortest = find_path(map, start, end, map.find_shortest_path)
    create_and_display_map(shortest, "Shortest Path")

    print("Finding multipath")
    all_paths = find_path(map, start, end, map.find_all_paths)
    for i, path in enumerate(all_paths):
        print(f"Length of path: {len(path)}")
        create_and_display_map(path, str(i) + ". Path ")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    standalone_example()
