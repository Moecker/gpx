import logging
import math
import os
import pickle
from collections import defaultdict
from functools import partial
from pathlib import Path
from pprint import pformat

import networkx as nx
from joblib import Parallel, delayed
from tqdm import tqdm

import astar
import config
import cpp.graph.graph as graph_cpp
import cpp.point.point as point_cpp
import distance
import gpx_tools
import utils

global GLOBAL_SEGMENTS_DICT


def debug_graph(map):
    for node, neighbors in map.friends.items():
        logging.trace(node)
        for other_node, cost in neighbors.items():
            logging.trace(f"|- {other_node} at {cost:.2f} km")


def adjust_weight_foreign_segments(map):
    for node, neighbors in map.friends.items():
        key, _ = gpx_tools.deannotate(node)
        for other_node, cost in neighbors.items():
            other_key, _ = gpx_tools.deannotate(other_node)
            cost = cost["weight"] if config.USE_NETWORK_X else cost
            if key != other_key:
                map.adjust_weight(node, other_node, cost * config.COST_SWITCH_SEGMENT_PENALTY)
            else:
                map.adjust_weight(node, other_node, cost * config.COST_NORMAL_PENALTY)


def adjust_weight_of_path(path, map):
    old_weights = defaultdict(partial(defaultdict, int))
    prev_point = None
    for point in path:
        if prev_point == None:
            prev_point = point
            continue
        old_weights[prev_point][point] = map.get_weight(prev_point, point)
        map.adjust_weight(prev_point, point, config.COST_ALREADY_VISITED_PENALTY)
        prev_point = point
    return old_weights


def build_map_smart(segments_dict, map):
    with tqdm(total=len(segments_dict.items()), disable=logging.getLogger().level > logging.INFO) as pbar:
        for cur_name, cur_segment in segments_dict.items():
            pbar.set_description(f"Building {cur_name.ljust(180):.100s}")

            first_point = None
            has_connection = False

            intersection_point = None
            needs_intra = False
            for cur_point in cur_segment.points:

                if first_point == None:
                    first_point = cur_point

                for oth_name, oth_segment in segments_dict.items():
                    if cur_name != oth_name:
                        idx = 0
                        while idx < len(oth_segment.points):
                            oth_point = oth_segment.points[idx]
                            dis = distance.haversine_gpx(cur_point, oth_point)

                            if dis < config.GRAPH_CONNECTION_DISTANCE:
                                logging.trace(f"Segment change adding {cur_point} to {oth_point} with {dis:.2f} km")
                                map.add(cur_point, oth_point, max(1, int(dis)))

                                has_connection = True

                                if not intersection_point and first_point != cur_point:
                                    needs_intra = True
                                    dis = distance.haversine_gpx(first_point, cur_point)
                                    logging.trace(
                                        f"First inter segment adding {first_point} to {cur_point} with {dis:.2f} km"
                                    )
                                    map.add(first_point, cur_point, max(1, int(dis)))
                                    intersection_point = cur_point

                            if config.USE_INEXACT_STEP_DISTANCE:
                                step_distance = int(
                                    dis * 1000 / config.REDUCTION_DISTANCE / config.GRAPH_CONNECTION_DISTANCE
                                )
                            else:
                                step_distance = 1

                            # Jump the step size, but always add the last point, too.
                            # Break however, once reached.
                            if idx == len(oth_segment.points) - 1:
                                break
                            idx = min(idx + max(1, step_distance), max(len(oth_segment.points) - 1, 1))

                if needs_intra:
                    if intersection_point != cur_point:
                        dis = distance.haversine_gpx(intersection_point, cur_point)
                        logging.trace(f"Inter segment adding {intersection_point} to {cur_point} with {dis:.2f} km")
                        map.add(intersection_point, cur_point, max(1, int(dis)))
                        intersection_point = cur_point

            if not has_connection:
                dis = distance.haversine_gpx(first_point, cur_point)
                logging.trace(f"No intersection adding {first_point} to {cur_point} with {dis:.2f} km")
                map.add(first_point, cur_point, max(1, int(dis)))

            pbar.update(1)
        debug_graph(map)
    return map


def build_map(segments_dict, map):
    with tqdm(total=len(segments_dict.items()), disable=logging.getLogger().level > logging.INFO) as pbar:
        for name, segment in segments_dict.items():
            pbar.set_description(f"Building {name.ljust(180):.100s}")

            inner(segment, segments_dict, map)

            pbar.update(1)
    return map


def inner(segment, segments_dict, map):
    additions = []
    if not len(segment.points):
        logging.error("No points in segment.")
        return additions

    idx = 0
    prev_point = None
    while idx < len(segment.points):
        point = segment.points[idx]
        if prev_point:
            dis = distance.haversine_gpx(prev_point, point)
            map.add(prev_point, point, max(1, int(dis)))
            additions.append((prev_point, point, max(1, int(dis))))

        adjacent_additions = find_and_add_adjacent_nodes(map, segments_dict, segment, point)
        additions.extend(adjacent_additions)

        prev_point = point

        # Jump the step size, but always add the last point, too
        # Break however, once reached.
        if idx == len(segment.points) - 1:
            break
        idx = min(idx + max(1, config.PRECISION), max(len(segment.points) - 1, 1))
    return additions


def do_parallel(segment, segments_dict):
    additions = inner(segment, segments_dict, astar.Graph())
    return additions


def build_map_parallel(segments_dict, the_map):
    # This does not work (yet) as expected. Goal is to parallelize the
    # graph building proess.
    args = [(k, segments_dict) for k in list(segments_dict.values())]

    parallel_calls = tqdm([partial(do_parallel, segment, segments_dict) for segment, segments_dict in args])
    additions = Parallel(n_jobs=1)(delayed(f)() for f in parallel_calls)

    for addition_group in additions:
        for addition in addition_group:
            the_map.add(addition[0], addition[1], addition[2])
    return the_map


def build_map_smart_parallel(segments_dict, the_map):
    return build_map_parallel(segments_dict, the_map)


def build_map_cpp(segments_dict):
    map = graph_cpp.Graph()
    return build_map(segments_dict, map)


def compute_min_dis(map, start_gpx):
    min_dis = math.inf
    min_node = None

    nodes = map.keys()
    for k in nodes:
        k = map.get(k) if config.USE_CPP else k
        dis = distance.haversine_gpx(k, start_gpx)
        if dis < min_dis:
            min_dis = dis
            min_node = k
    return min_dis, min_node


def find_and_add_adjacent_nodes(map, segments_dict, current_segment, current_point):
    additions = []
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
                map.add(current_point, other_point, max(1, int(dis)))
                additions.append((current_point, other_point, max(1, int(dis))))

            if config.USE_INEXACT_STEP_DISTANCE:
                step_distance = int(dis * 1000 / config.REDUCTION_DISTANCE / config.GRAPH_CONNECTION_DISTANCE)
            else:
                step_distance = 1

            # Jump the step size, but always add the last point, too.
            # Break however, once reached.
            if idx == len(other_segment.points) - 1:
                break
            idx = min(idx + max(1, step_distance), max(len(other_segment.points) - 1, 1))
    return additions


def find_path(map, start, end, strategy):
    first, last = get_closest_start_and_end(map, start, end)

    if not first or not last:
        logging.error(f"Start and/or End GPX positions are invalid.")
        return None

    if first == last:
        logging.warning(f"Start and End GPX positions are identical.")
        return None

    logging.info("Searching Path.")
    path, cost = strategy(first, last)

    if not path:
        logging.warning(f"No path found from {first} to {last}.")
        return None

    logging.debug(f"Path found, length of path: {len(path)}.")
    logging.debug(f"Path found, cost of path: {cost}.")
    logging.info(f"Found Path of length {len(path)} and cost {cost}.")
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
    if not config.USE_PICKLE or config.ALWAYS_GRAPH or not os.path.isfile(pickle_path):
        logging.debug(f"Pickle file {pickle_path} does not exist or is forced ignored, creating map.")

        # Decide which graph implementation to use.
        map = graph_cpp.Graph() if config.USE_CPP else astar.Graph()

        # Decide which graph build algo to use.
        if config.USE_PARALLEL:
            map = (
                build_map_smart_parallel(segments_dict, map)
                if config.USE_SMART
                else build_map_parallel(segments_dict, map)
            )
        else:
            map = build_map_smart(segments_dict, map) if config.USE_SMART else build_map(segments_dict, map)

        if config.USE_NETWORK_X:
            map = nx.Graph((k, v, {"weight": weight}) for k, vs in map.friends.items() for v, weight in vs.items())

        if config.USE_PICKLE:
            logging.debug(f"Saving pickle file to '{utils.make_path_clickable(pickle_path)}'.")
            Path(pickle_path).resolve().parent.mkdir(parents=True, exist_ok=True)
            with open(pickle_path, "wb") as f:
                pickle.dump(map, f)

    if config.USE_PICKLE:
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

    previous_idx = None
    previous_key = None

    prev_point = None
    is_reversed = False

    batch_points = []
    rescaled_path = []

    for i, point in enumerate(path):
        if not point.annotation:
            logging.warning(f"Cannot rescale because annotations are missing, skipping.")
            return rescaled_path

        key, idx = gpx_tools.deannotate(point)

        # We saw a new section or we are at the beginning.
        if key != previous_key:
            used_segments.append(key)
            previous_key = key

            # Unclear why this is producing artifacts in "normal" mode.
            # The edge cases seem to not work correctly (first, last point of segment and entire path)
            if config.IS_TEST:
                if not is_reversed:
                    if prev_point:
                        rescaled_path.append(prev_point)
                    rescaled_path.extend(batch_points)
                else:
                    rescaled_path.extend(batch_points)
                    if prev_point:
                        rescaled_path.append(prev_point)
            else:
                rescaled_path.extend(batch_points)

            batch_points = []
            prev_point = segments_dict[key].points[idx]
        else:
            is_reversed = previous_idx < idx
            if is_reversed:
                adding_points = segments_dict[key].points[previous_idx:idx]
                prev_point = segments_dict[key].points[idx]
            else:
                adding_points = segments_dict[key].points[idx:previous_idx]
                adding_points = reversed(adding_points)
                prev_point = segments_dict[key].points[previous_idx]

            batch_points.extend(adding_points)

        previous_idx = idx

        # Last point.
        if i == len(path) - 1:
            if config.IS_TEST:
                if not is_reversed:
                    if prev_point:
                        rescaled_path.append(prev_point)
                    rescaled_path.extend(batch_points)
                else:
                    rescaled_path.extend(batch_points)
                    if prev_point:
                        rescaled_path.append(prev_point)
            else:
                rescaled_path.extend(batch_points)

    if not len(rescaled_path):
        logging.error(f"Rescaling failed, could not determine points.")
        return None

    logging.debug(f"Rescaled from {len(path)} to {len(rescaled_path)} points.")

    logging.info(f"Path uses {len(used_segments)} different segments.")
    logging.debug(f"Used segments: \n{pformat(used_segments)}.")

    return rescaled_path
