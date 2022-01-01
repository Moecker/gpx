import logging
import math
import os
import pickle
from pathlib import Path
from pprint import pformat

from tqdm import tqdm

import config
import distance
import gpx_tools
import utils


def debug_graph(map):
    for node, neighbors in map.friends.items():
        logging.trace(node)
        for other_node, cost in neighbors.items():
            logging.trace("| " + str(other_node) + ":" + str(cost))


def adjust_weight_foreign_segments(map):
    for node, neighbors in map.friends.items():
        key, idx = gpx_tools.deannotate(node)
        for other_node, cost in neighbors.items():
            other_key, other_idx = gpx_tools.deannotate(other_node)
            if key != other_key:
                map.adjust_weight(node, other_node, cost * config.COST_SWITCH_SEGMENT_PENALTY)
            else:
                map.adjust_weight(node, other_node, cost * config.COST_NORMAL_PENALTY)


def adjust_weight_of_path(path, map):
    prev_point = None
    for point in path:
        if prev_point == None:
            prev_point = point
            continue
        map.adjust_weight(prev_point, point, config.COST_ALREADY_VISITED_PENALTY)
        prev_point = point


def build_map_smart(segments_dict):
    map = config.GRAPH_MODUL.Graph()
    for cur_name, cur_segment in segments_dict.items():
        first_point = None
        has_connection = False

        for cur_point in cur_segment.points:
            if not first_point:
                first_point = cur_point

            for oth_name, oth_segment in segments_dict.items():
                for oth_point in oth_segment.points:
                    if cur_name != oth_name:
                        dis = distance.haversine_gpx(cur_point, oth_point)
                        if dis < config.GRAPH_CONNECTION_DISTANCE:
                            logging.trace(f"Normal adding {cur_point.short()} to {oth_point.short()} with {dis:.2f} km")
                            map.add(cur_point, oth_point, dis)
                            has_connection = True

        if not has_connection:
            dis = distance.haversine_gpx(first_point, cur_point)
            map.add(first_point, cur_point, dis)

    return map


def build_map(segments_dict):
    map = config.GRAPH_MODUL.Graph()

    with tqdm(total=len(segments_dict.items()), disable=logging.getLogger().level > logging.INFO) as pbar:
        for name, segment in segments_dict.items():
            pbar.set_description(f"Building {name.ljust(180):.100s}")

            if not len(segment.points):
                continue

            idx = 0
            prev_point = None
            while idx < len(segment.points):
                point = segment.points[idx]
                if prev_point:
                    dis = distance.haversine_gpx(prev_point, point)

                    assert prev_point != point

                    map.add(prev_point, point, cost=max(1, int(dis)))

                prev_point = point
                find_and_add_adjacent_nodes(map, segments_dict, segment, point)

                # Jump the step size, but always add the last point, too
                # Break however, once reached.
                if idx == len(segment.points) - 1:
                    break
                idx = min(idx + max(1, config.PRECISION), max(len(segment.points) - 1, 1))
            pbar.update(1)
    return map


def collect_all_points(segments_dict):
    all_points = []
    for _, segment in segments_dict.items():
        for point in segment.points:
            all_points.append(point)
    return all_points


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


def find_and_add_adjacent_nodes(map, segments_dict, current_segment, current_point):
    for _, other_segment in segments_dict.items():
        # Do no connect points which would skip intermediate, intra segment points
        if other_segment == current_segment:
            continue

        if not len(other_segment.points):
            continue

        idx = 0
        while idx < len(other_segment.points):
            other_point = other_segment.points[idx]
            dis = distance.haversine_gpx(current_point, other_point)

            assert current_point != other_point

            if dis < config.GRAPH_CONNECTION_DISTANCE:
                map.add(current_point, other_point, cost=max(1, int(dis)))

            if config.USE_INEXACT_STEP_DISTANCE:
                step_distance = int(dis * 1000 / config.REDUCTION_DISTANCE / config.GRAPH_CONNECTION_DISTANCE)
            else:
                step_distance = 1

            # Jump the step size, but always add the last point, too.
            # Break however, once reached.
            if idx == len(other_segment.points) - 1:
                break
            idx = min(idx + max(1, step_distance), max(len(other_segment.points) - 1, 1))


def find_path(map, start, end, strategy):
    first, last = get_closest_start_and_end(map, start, end)

    if not first or not last:
        logging.error(f"Start and/or End GPX positions are invalid.")
        return None

    if first == last:
        logging.error(f"Start and End GPX positions are identical.")
        return None

    logging.debug(f"Starting search strategy using {strategy}.")
    path, cost = strategy(first, last)
    if not path:
        logging.error(f"No path found from {first} to {last}.")
        return None

    logging.debug(f"Path found, length of path: {len(path)}.")
    logging.debug(f"Path found, cost of path: {cost}.")
    logging.info(f"Found Path of (node-)length {len(path)} and (graph-)cost {cost}.")
    return path


def get_closest_start_and_end(map, start_gpx, end_gpx):
    min_dis_start, first = compute_min_dis(map, start_gpx)
    min_dis_end, last = compute_min_dis(map, end_gpx)

    logging.debug(f"Desired GPS start: {start_gpx} and end: {end_gpx}.")
    logging.debug(f"Minimum distance to start: {min_dis_start:.2f} km, and end: {min_dis_end:.2f} km")
    logging.info(f"Closest possible GPS start node with distance {min_dis_start:.2f} km in graph is: {first}")
    logging.info(f"Closest possible GPS end node with distance {min_dis_end:.2f} km in graph is: {last}")

    return first, last


def load_or_build_map(segments_dict, name, output_dir):
    pickle_path = os.path.join(output_dir, name)
    if config.ALWAYS_GRAPH or not os.path.isfile(pickle_path):
        logging.debug(f"Pickle file {pickle_path} does not exist or is forced ignored, creating map.")

        if config.USE_SMART:
            map = build_map_smart(segments_dict)
        else:
            map = build_map(segments_dict)

        logging.debug(f"Saving pickle file to '{utils.make_path_clickable(pickle_path)}'.")
        Path(pickle_path).resolve().parent.mkdir(parents=True, exist_ok=True)
        with open(pickle_path, "wb") as f:
            pickle.dump(map, f)

    logging.debug(f"Pickle file '{utils.make_path_clickable(pickle_path)}' exist.")
    logging.debug(f"Loading '{utils.make_path_clickable(pickle_path)}'.")
    with open(pickle_path, "rb") as f:
        map = pickle.load(f)

    return map


def rescale(segments_dict, path):
    used_segments = []
    if not path:
        logging.warning(f"Cannot rescale, because path is empty.")
        return None

    if len(path) < 2:
        logging.warning(f"Cannot rescale, because path must have at least 3 points.")
        return None

    if len(path) == 2:
        return path

    previous_idx = None
    previous_key = None
    batch_points = []

    rescaled_path = []

    prev_point = None
    for i, point in enumerate(path):
        if not point.annotation:
            logging.warning(f"Cannot rescale because annotations are missing, skipping.")
            return None

        key, idx = gpx_tools.deannotate(point)

        # We saw a new section
        if key != previous_key:
            used_segments.append(key)
            previous_key = key
            if prev_point:
                rescaled_path.append(prev_point)
            rescaled_path.extend(batch_points)
        else:
            # Importantly, the original tour can be made in both directions.
            # To respect this, the found part-segments have to be added
            # not according to how it has ben recorded, but how the current
            # direction is.
            if previous_idx < idx:
                adding_points = segments_dict[key].points[previous_idx:idx]
                prev_point = segments_dict[key].points[idx]
            else:
                adding_points = segments_dict[key].points[idx:previous_idx]
                adding_points = reversed(adding_points)
                prev_point = segments_dict[key].points[previous_idx]

            batch_points.extend(adding_points)

        previous_idx = idx

        if i == len(path) - 1:
            rescaled_path.extend(batch_points)
            rescaled_path.append(prev_point)

    if not len(rescaled_path):
        logging.error(f"Rescaling failed, could not determine points.")
        return None

    logging.debug(f"Rescaled from {len(path)} to {len(rescaled_path)} points.")
    logging.info(f"Path uses {len(used_segments)} different segments.")
    logging.debug(f"Used segments: \n{pformat(used_segments)}.")
    return rescaled_path
