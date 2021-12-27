import glob
import logging
import math
import os
import pickle
from pathlib import Path
from pprint import pformat

import gpxpy
import gpxpy.gpx

from tqdm import tqdm

import config
import distance
import gpx_tools
import reducer
import walk


def determine_start():
    munich_gps = gpxpy.gpx.GPXTrackPoint(48.13743, 11.57549)
    return munich_gps


def determine_end():
    dachau_gps = gpxpy.gpx.GPXTrackPoint(48.26299, 11.43390)
    return dachau_gps


def determine_reduction_threshold():
    return config.REDUCTION_DISTANCE


def determine_possible_end_and_start_distance(start_gps, end_gps, segments_dict):
    distances_start = compute_distances(start_gps, segments_dict)
    distances_end = compute_distances(end_gps, segments_dict)

    distances_start = sorted(distances_start.items(), key=lambda x: x[1])
    distances_end = sorted(distances_end.items(), key=lambda x: x[1])

    logging.debug("Start distances \n" + pformat(distances_start, width=240))
    logging.debug("End distances \n" + pformat(distances_end, width=240))

    logging.info(f"Closest possible start {distances_start[0][1]:.2f} km.")
    logging.info(f"Closest possible end {distances_end[0][1]:.2f} km.")
    return distances_start, distances_end


def try_load_pickle(pickle_path):
    if not config.ALWAYS_PARSE and os.path.isfile(pickle_path):
        logging.info(f"{pickle_path} exists, using it.")
        segments_dict = pickle.load(open(pickle_path, "rb"))
        return segments_dict
    else:
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


def load_and_reduce_gpxs(track_file_names, threshold, pickle_path, output_dir):
    logging.info(f"{pickle_path} does not exist or is forced ignored, creating it.")

    segments_dict = dict()
    threshold_string = str(int(threshold))
    dir_name = os.path.join(output_dir, threshold_string)
    Path(dir_name).mkdir(parents=True, exist_ok=True)

    pbar = tqdm(track_file_names)
    for track_file_name in pbar:
        track_file_name_reduced = os.path.join(
            dir_name, threshold_string + "_" + track_file_name.replace(os.path.sep, "_")
        )

        if config.ALWAYS_REDUCE or not os.path.isfile(track_file_name_reduced):
            pbar.set_description(f"INFO: {track_file_name_reduced} does not exist or is forced ignored, creating it.")
            success = reducer.reduce(track_file_name, threshold, track_file_name_reduced)
            if not success:
                continue
        else:
            pbar.set_description(f"INFO: {track_file_name_reduced} exists, using it.")

        setup_segments_dict(segments_dict, track_file_name_reduced)
    return segments_dict


def setup_segments_dict(segments_dict, track_file_name_reduced):
    with open(track_file_name_reduced, "r") as f:
        gpx = gpxpy.parse(f)
        for track in gpx.tracks:
            segment_id = 0
            for segment in track.segments:
                key = track_file_name_reduced + ":" + track.name + ":" + str(segment_id)
                segments_dict[key] = gpx_tools.simplify_segment(segment)
                segment_id += 1


def build_segments_dict(reduction_threshold, pickle_path, root, output_dir):
    segments_dict = try_load_pickle(pickle_path)

    if not segments_dict:
        track_file_names = glob.glob(root)
        logging.info(f"Globing found {len(track_file_names)} files.")
        segments_dict = load_and_reduce_gpxs(track_file_names, reduction_threshold, pickle_path, output_dir)
        logging.info(f"Saving pickle file to {pickle_path}.")
        pickle.dump(segments_dict, open(pickle_path, "wb"))
    logging.info(f"Found {len(segments_dict)} segment(s).")
    return segments_dict
