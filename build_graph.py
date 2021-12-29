import logging
import math
import os
import pickle
from pathlib import Path
from pprint import pformat

from tqdm import tqdm

import config
import distance
import gpx2ascii
import gpx_tools
import points2ascii


def annotate(point, name, idx):
    point.annotation = f"{name}@{idx}"


def deannotate(point):
    annotations = point.annotation.split("@")
    key = annotations[0]
    idx = int(annotations[1])
    return key, idx


def build_map(segments_dict):
    map = config.GRAPH_MODUL.Graph()
    pbar = tqdm(segments_dict.items())
    for name, segment in pbar:
        pbar.set_description(f"INFO: Processing {name.ljust(180):.100s} with {len(segment.points):6d} points.")

        if not len(segment.points):
            continue

        idx = 0
        prev_point = None
        while idx < len(segment.points):
            point = segment.points[idx]
            if prev_point:
                dis = distance.haversine_gpx(prev_point, point)
                map.add(prev_point, point, cost=int(dis + config.COST_NORMAL_PENALTY))

            prev_point = point
            find_and_add_adjacent_nodes(map, segments_dict, segment, point)

            # Jump the step size, but always add the last point, too
            # Break however, once reached.
            if idx == len(segment.points) - 1:
                break
            idx = min(idx + max(1, config.PRECISION), max(len(segment.points) - 1, 1))
    return map


def find_and_add_adjacent_nodes(map, segments_dict, current_segment, current_point):
    for name, other_segment in segments_dict.items():
        # Do no connect points which would skip intermediate, intra segment points
        if other_segment == current_segment:
            continue

        if not len(other_segment.points):
            continue

        idx = 0
        while idx < len(other_segment.points):
            other_point = other_segment.points[idx]
            dis = distance.haversine_gpx(current_point, other_point)

            if dis < config.GRAPH_CONNECTION_DISTANCE:
                map.add(current_point, other_point, cost=int(dis + config.COST_SWITCH_SEGMENT_PENALTY))

            step_distance = int(dis * 1000 / config.REDUCTION_DISTANCE / config.GRAPH_CONNECTION_DISTANCE)

            # Jump the step size, but always add the last point, too.
            # Break however, once reached.
            if idx == len(other_segment.points) - 1:
                break
            idx = min(idx + max(1, step_distance), max(len(other_segment.points) - 1, 1))


def add_waypoints(map, path, edges, character):
    for point in path[::]:
        idx_w, idx_h = gpx2ascii.determine_index((point.latitude, point.longitude), edges)
        idx_w = min(idx_w, len(map) - 1)

        assert idx_w < len(map), f"{idx_w} exceeds {len(map)}"
        assert len(map) > 0
        assert idx_h < len(map[0])

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


def get_closest_start_and_end(map, start_gpx, end_gpx):
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
        Path(pickle_path).resolve().parent.mkdir(parents=True, exist_ok=True)
        pickle.dump(map, open(pickle_path, "wb"))

    logging.info(f"Pickle {pickle_path} exist, using it.")
    logging.info(f"Loading {pickle_path}...")
    map = pickle.load(open(pickle_path, "rb"))

    return map


def rescale(segments_dict, path):
    used_segments = []
    if not path:
        logging.warning(f"Cannot rescale because path is empty, skipping.")
        return None

    previous_idx = None
    previous_key = None

    rescaled_path = []

    for point in path:
        if not point.annotation:
            logging.warning(f"Cannot rescale because annotations are missing, skipping.")
            return None

        key, idx = deannotate(point)

        if key != previous_key:
            used_segments.append(key)
            previous_idx = None
            previous_key = key

        if not previous_idx:
            previous_idx = idx
            continue

        # Importantly, the original tour can be made in both directions.
        # To respect this, the found part-segments have to be added
        # not according to how it has ben recorded, but how the current
        # direction is.
        if previous_idx < idx:
            adding_points = segments_dict[key].points[previous_idx:idx]
            logging.debug(f"Adding range: {previous_idx}:{idx}:{key}")
        else:
            adding_points = segments_dict[key].points[idx:previous_idx]
            adding_points = reversed(adding_points)
            logging.debug(f"Adding range: {idx}:{previous_idx}:{key}")

        rescaled_path.extend(adding_points)

        segments_dict[key]
        previous_idx = idx

    if not len(rescaled_path):
        logging.error(f"Rescaling failed, could not determine points.")
        return None

    logging.info(f"Rescaled from {len(path)} to {len(rescaled_path)} points.")
    logging.info(f"Used {len(used_segments)} different segments")
    logging.debug(f"Used segments: \n{pformat(used_segments)}")
    return rescaled_path


def adjust_weight_of_path(path, map):
    prev_point = None
    for point in path:
        if prev_point == None:
            prev_point = point
            continue
        map.adjust_weight(prev_point, point, 10 * 1000)
        prev_point = point
