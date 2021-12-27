import logging
import math
import os
import pickle

from tqdm import tqdm

import build_segments
import config
import distance
import gpx2ascii
import gpx_tools
import graph
import points2ascii


def build_map(segments_dict):
    map = graph.Graph()
    pbar = tqdm(segments_dict.items())
    for name, segment in pbar:
        pbar.set_description(f"INFO: Processing {name} with {len(segment.points)} points.")
        if len(segment.points):
            prev_point = None
            for point in segment.points[:: config.PRECISION]:
                # Direct, inter segment connection is always possible, without checking the distance
                if prev_point:
                    dis = distance.haversine_gpx(prev_point, point)
                    assert (
                        dis < config.TOLERATION_DISTANCE
                    ), f"Distance {dis:.2f} greater than {config.TOLERATION_DISTANCE}"

                    assert dis > 0, f"Distance between {prev_point} and {point} should not be zero"

                    map.add(prev_point, point, cost=int(dis + config.COST_NORMAL_PENALTY))

                prev_point = point
                # find_and_add_adjacent_nodes(map, segments_dict, segment, point)
    return map


def find_and_add_adjacent_nodes(map, segments_dict, current_segment, current_point):
    for _, other_segment in segments_dict.items():
        # Do no connect points which would skip intermediate, intra segment points
        if other_segment == current_segment:
            continue
        for other_point in other_segment.points[:: config.PRECISION * config.PRECISION_OTHER_SEGMENT]:
            # Self connection does not make sense
            if current_point == other_point:
                continue
            dis = distance.haversine_gpx(current_point, other_point)
            if dis < config.GRAPH_CONNECTION_DISTANCE:
                map.add(current_point, other_point, cost=int(dis + config.COST_SWITCH_SEGMENT_PENALTY))


def add_waypoints(map, path, edges, character):
    for point in path:
        idx_w, idx_h = gpx2ascii.determine_index((point.latitude, point.longitude), edges)
        map[idx_w][idx_h] = character


def create_and_display_map(path, name, background=[]):
    if not path:
        logging.warning(f"Nothing to display for '{name}', no valid points.")
        return

    logging.info(f"Creating map '{name}'...")
    edges = points2ascii.determine_bounding_box(path + background)
    map = points2ascii.create_map(edges, " ")

    add_waypoints(map, background, edges, ".")
    add_waypoints(map, path, edges, "x")

    logging.info(f"Displaying map name: {name}.")
    gpx2ascii.display(map)


def compute_min_dis(map, start_gpx):
    min_dis = math.inf
    min_node = None
    for k, _ in map.edges.items():
        dis = distance.haversine_gpx(k, start_gpx)
        if dis < min_dis:
            min_dis = dis
            min_node = k
    return min_dis, min_node


def get_closest_start_and_end(map, start, end):
    start_gpx = gpx_tools.SimplePoint(start)
    end_gpx = gpx_tools.SimplePoint(end)

    min_dis_start, first = compute_min_dis(map, start_gpx)
    min_dis_end, last = compute_min_dis(map, end_gpx)

    logging.info(f"Desired GPS start: {start_gpx} and end: {end_gpx}.")
    logging.info(f"Minimum distance to start: {min_dis_start:.2f} km, and end: {min_dis_end:.2f} km")
    logging.info(f"Closest GPS node for start: {first} and end: {last}.")

    return first, last


def find_path(map, start, end, strategy):
    first, last = get_closest_start_and_end(map, start, end)

    if not first or not last:
        logging.error(f"Start and/or End GPX positions are invalid.")
        return None

    path = strategy(first, last)
    if not path:
        logging.error(f"No path found from {first} to {last}.")
        return None

    logging.info(f"Path(s) found, length of path(s): {len(path)}.")
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
        logging.info(f"Pickle {pickle_path} does not exist or is forced ignored, creating map.")
        map = build_map(segments_dict)

        logging.info(f"Saving pickle file to {pickle_path}.")
        pickle.dump(map, open(pickle_path, "wb"))

    logging.info(f"Pickle {pickle_path} exist, using it.")
    logging.info(f"Loading {pickle_path}...")
    map = pickle.load(open(pickle_path, "rb"))

    return map
