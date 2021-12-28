import logging
import math
import os
import pickle

from tqdm import tqdm

import config
import distance
import gpx2ascii
import gpx_tools
import points2ascii


def annotate(point, name, idx):
    point.annotation = f"{name}@{idx}"


def build_map(segments_dict):
    map = config.GRAPH_MODUL.Graph()
    pbar = tqdm(segments_dict.items())
    for name, segment in pbar:
        pbar.set_description(f"INFO: Processing {name} with {len(segment.points)} points.")
        if len(segment.points):
            if config.USE_SMART_ALGO:
                idx = 0
                prev_point = None
                while idx < len(segment.points):
                    point = segment.points[idx]
                    annotate(point, name, idx)

                    if prev_point:
                        dis = distance.haversine_gpx(prev_point, point)
                        map.add(prev_point, point, cost=int(dis + config.COST_NORMAL_PENALTY))

                    prev_point = point
                    find_and_add_adjacent_nodes(map, segments_dict, segment, point)
                    idx = idx + max(1, config.PRECISION)
            else:
                # TODO Consider removing this
                prev_point = None
                for _, point in enumerate(segment.points[:: config.PRECISION]):
                    # Direct, inter segment connection is always possible, without checking the distance
                    if prev_point:
                        dis = distance.haversine_gpx(prev_point, point)
                        map.add(prev_point, point, cost=int(dis + config.COST_NORMAL_PENALTY))
                    prev_point = point
                    find_and_add_adjacent_nodes(map, segments_dict, segment, point)

    return map


def find_and_add_adjacent_nodes(map, segments_dict, current_segment, current_point):
    for name, other_segment in segments_dict.items():
        # Do no connect points which would skip intermediate, intra segment points
        if other_segment == current_segment:
            continue

        if config.USE_SMART_ALGO:
            idx = 0
            while idx < len(other_segment.points):
                other_point = other_segment.points[idx]
                annotate(other_point, name, idx)

                dis = distance.haversine_gpx(current_point, other_point)

                # TODO Consider using this to enable more points
                # TODO step_distance = int(dis * 1000 / config.REDUCTION_DISTANCE / config.GRAPH_CONNECTION_DISTANCE)
                step_distance = int(dis * 1000 / config.REDUCTION_DISTANCE)
                idx = idx + max(1, step_distance)

                if dis < config.GRAPH_CONNECTION_DISTANCE:
                    map.add(current_point, other_point, cost=int(dis + config.COST_SWITCH_SEGMENT_PENALTY))
        else:
            # TODO Consider removing this
            for other_point in other_segment.points[:: config.PRECISION]:
                # Self connection does not make sense
                if current_point == other_point:
                    continue
                dis = distance.haversine_gpx(current_point, other_point)
                if dis < config.GRAPH_CONNECTION_DISTANCE:
                    map.add(current_point, other_point, cost=int(dis + config.COST_SWITCH_SEGMENT_PENALTY))


def add_waypoints(map, path, edges, character):
    for point in path[:: config.SCALE_FACTOR]:
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

    logging.info(f"Displaying map name: '{name}'.")
    gpx2ascii.display(map)


def compute_min_dis(map, start_gpx):
    min_dis = math.inf
    min_node = None
    nodes = map.keys()
    for k in nodes:
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

    logging.info(f"Starting search strategy using {strategy}...")
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


def rescale(segments_dict, path):
    if not path:
        logging.warning(f"Cannot rescale because path is empty, skipping")
        return None

    previous_idx = None
    previous_key = None

    rescaled_path = []

    for point in path:
        if not point.annotation:
            logging.warning(f"Cannot rescale because annotations are missing, skipping")
            return None

        annotations = point.annotation.split("@")
        key = annotations[0]
        idx = int(annotations[1])

        if key != previous_key:
            previous_idx = None
            previous_key = key

        if not previous_idx:
            previous_idx = idx
            continue

        if previous_idx < idx:
            adding_points = segments_dict[key].points[previous_idx:idx]
        else:
            adding_points = segments_dict[key].points[idx:previous_idx]

        rescaled_path.extend(adding_points)
        logging.debug(f"{previous_idx}:{idx}{key}")

        segments_dict[key]
        previous_idx = idx

    logging.info(f"Rescaled from {len(path)} to {len(rescaled_path)} points")
    return rescaled_path
