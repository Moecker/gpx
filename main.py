import glob
import logging
import math
import os
import pickle
from pprint import pformat

import gpxpy
import gpxpy.gpx

import config
import distance
import reducer
import utils


def determine_start():
    munich_gps = gpxpy.gpx.GPXTrackPoint(48.13743, 11.57549)
    return munich_gps


def determine_end():
    dachau_gps = gpxpy.gpx.GPXTrackPoint(48.26299, 11.43390)
    berlin_gps = gpxpy.gpx.GPXTrackPoint(52.520007, 13.404954)
    return dachau_gps


def determine_reduction_threshold():
    return config.REDUCTION_DISTANCE


def try_load_pickle(pickle_path):
    if not config.ALWAYS_PARSE and os.path.isfile(pickle_path):
        logging.info(f"{pickle_path} exists, using it.")
        segments_dict = pickle.load(open(pickle_path, "rb"))
        return segments_dict
    else:
        logging.info(f"{pickle_path} exists, using it.")
        return None


def compute_distances(start_gps, segments_dict):
    distances = dict()
    for name, segment in segments_dict.items():
        min_distance = math.inf
        for point in segment.points:
            dis = distance.haversine_gpx(point, start_gps)
            if dis < min_distance:
                min_distance = dis
        logging.debug(f"Minimum Distance: {min_distance:.2f} km.")
        distances[name] = min_distance
    return distances


def load_and_reduce_gpxs(track_file_names, threshold, pickle_path):
    logging.warning(f"{pickle_path} does not exist or is forced ignored, creating it.")

    segments_dict = dict()
    for track_file_name in track_file_names:
        threshold_string = str(int(threshold))
        track_file_name_reduced = os.path.join(
            "output", threshold_string, threshold_string + "_" + track_file_name.replace(os.path.sep, "_")
        )

        if config.ALWAYS_REDUCE or not os.path.isfile(track_file_name_reduced):
            logging.warning(f"{track_file_name_reduced} does not exist or is forced ignored, creating it.")
            try:
                reducer.reduce(track_file_name, threshold, track_file_name_reduced)
            except:
                logging.error(f"Error while reducing {track_file_name} to create {track_file_name_reduced}.")
                continue
        else:
            logging.info(f"{track_file_name_reduced} exists, using it.")

        with open(track_file_name_reduced, "r") as f:
            gpx = gpxpy.parse(f)
            for track in gpx.tracks:
                segment_id = 0
                for segment in track.segments:
                    segments_dict[track_file_name_reduced + ":" + track.name + ":" + str(segment_id)] = segment
                    segment_id += 1
    return segments_dict


def determine_possible_end_and_start_distance(start_gps, end_gps, segments_dict):
    distances_start = compute_distances(start_gps, segments_dict)
    distances_end = compute_distances(end_gps, segments_dict)

    distances_start = sorted(distances_start.items(), key=lambda x: x[1])
    distances_end = sorted(distances_end.items(), key=lambda x: x[1])

    logging.debug("Start distances \n" + pformat(distances_start, width=240))
    logging.debug("End distances \n" + pformat(distances_end, width=240))

    logging.info(f"Closest possible start {distances_start[0][1]:.2f} km")
    logging.info(f"Closest possible end {distances_end[0][1]:.2f} km")
    return distances_start, distances_end


def walk_gpx(walk_segment_name, segments_dict, min_end_distance, end_gps, route, routes, current_distance):
    if len(routes) >= config.ROUTES_FOUND_END:
        return

    if walk_segment_name in segments_dict.keys():
        walk_segment = segments_dict[walk_segment_name]
        route.append(walk_segment_name)
    else:
        logging.debug(f"Skipping {utils.simple_name(walk_segment_name)}, has been seen before.")
        return

    segments_dict.pop(walk_segment_name)

    logging.debug(f"Walking {len(walk_segment.points)} points on {walk_segment_name}.")

    for walk_point in walk_segment.points[:: config.POINTS_ITERATOR_GAP]:
        for name, segment in segments_dict.copy().items():
            if name != walk_segment_name:
                for idx, point in enumerate(segment.points[:: config.POINTS_ITERATOR_GAP]):
                    dist = distance.haversine_gpx(walk_point, point)

                    if dist < config.MIN_GAP_DIS:
                        logging.debug(
                            f"Switch from {utils.simple_name(walk_segment_name)} to {utils.simple_name(name)} at point id {idx} possible distanced by {dist} km."
                        )
                        walk_gpx(name, segments_dict, min_end_distance, end_gps, route, routes, current_distance)
                        break

        to_end_dist = distance.haversine_gpx(walk_point, end_gps)
        if to_end_dist < (min_end_distance + config.MAX_END_DISTANCE):
            tupled = tuple(route)
            if not tupled in routes:
                routes.add(tuple(route))
                logging.info(f"New route found following {pformat(route)}.")

        if to_end_dist < current_distance:
            current_distance = to_end_dist

        if to_end_dist > (current_distance + config.MAX_DETOUR):
            logging.debug(f"Detour of {to_end_dist} km to end, skipping.")
            return


def main():
    start_gps = determine_start()
    end_gps = determine_end()
    reduction_threshold = determine_reduction_threshold()

    country = "at"
    pickle_path = os.path.join("pickle", country + "_" + str(int(reduction_threshold)) + "_" + "segments.p")
    segments_dict = try_load_pickle(pickle_path)

    if not segments_dict:
        track_file_names = glob.glob(os.path.join("bikeline", country, config.GPX_FILE_PATTERN))
        segments_dict = load_and_reduce_gpxs(track_file_names, reduction_threshold, pickle_path)
        pickle.dump(segments_dict, open(pickle_path, "wb"))
    logging.info(f"Found {len(segments_dict)} segments")

    distances_start, distances_end = determine_possible_end_and_start_distance(start_gps, end_gps, segments_dict)

    routes = set(tuple())
    route = list()
    current_distance = math.inf

    walk_gpx(distances_start[0][0], segments_dict, distances_start[0][1], end_gps, route, routes, current_distance)

    logging.info(f"Found {len(routes)} routes")
    logging.info(f"Found those routes \n{pformat(routes)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
