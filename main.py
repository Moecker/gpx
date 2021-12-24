import gpxpy
import gpxpy.gpx
import distance
import math
import os
import reducer
import logging
from pprint import pformat
import glob
import pickle
import config


def determine_start():
    munich_gps = gpxpy.gpx.GPXTrackPoint(48.13743, 11.57549)
    return munich_gps


def determine_end():
    enschau_gps = gpxpy.gpx.GPXTrackPoint(47.31107, 13.00691)
    return enschau_gps


def determine_reduction_threshold():
    return 500.0


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
        logging.debug(f"Minimum Distance: {min_distance:.2f} km")
        distances[name] = min_distance
    return distances


def load_and_reduce_gpxs(track_file_names, threshold, pickle_path):
    logging.warning(f"{pickle_path} does not exist or is forced ignored, creating it.")

    segments_dict = dict()
    for track_file_name in track_file_names:
        threshold_string = str(int(threshold))
        track_file_name_reduced = os.path.join(
            "output", threshold_string, threshold_string + "_" + track_file_name.replace("/", "_")
        )

        if config.ALWAYS_REDUCE or not os.path.isfile(track_file_name_reduced):
            logging.warning(f"{track_file_name_reduced} does not exist or is forced ignored, creating it.")
            try:
                reducer.reduce(track_file_name, threshold, track_file_name_reduced)
            except:
                logging.error(f"Error while reducing {track_file_name} to create {track_file_name_reduced}")
                continue
        else:
            logging.info(f"{track_file_name_reduced} exists, using it.")

        with open(track_file_name_reduced, "r") as f:
            gpx = gpxpy.parse(f)
            segment_id = 0
            for track in gpx.tracks:
                for segment in track.segments:
                    segments_dict[track_file_name_reduced + ":" + track.name + ":" + str(segment_id)] = segment
                    segment_id += 1
    return segments_dict


def walk_gpx(segment):
    for point in segment.points:
        pass


def main():
    start_gps = determine_start()
    end_gps = determine_end()
    reduction_threshold = determine_reduction_threshold()

    pickle_path = os.path.join("pickle", "segments.p")
    segments_dict = try_load_pickle(pickle_path)

    if not segments_dict:
        track_file_names = glob.glob("bikeline/at/*1.gpx")
        segments_dict = load_and_reduce_gpxs(track_file_names, reduction_threshold, pickle_path)
        pickle.dump(segments_dict, open(pickle_path, "wb"))
    logging.info(f"Found {len(segments_dict)} segments")

    distances_start, distances_end = determine_possible_end_and_start_distance(start_gps, end_gps, segments_dict)

    walk_gpx(segments_dict[distances_start[0][0]])
    walk_gpx(segments_dict[distances_end[0][0]])


def determine_possible_end_and_start_distance(start_gps, end_gps, segments_dict):
    distances_start = compute_distances(start_gps, segments_dict)
    distances_end = compute_distances(end_gps, segments_dict)

    distances_start = sorted(distances_start.items(), key=lambda x: x[1])
    distances_end = sorted(distances_end.items(), key=lambda x: x[1])

    logging.debug("\n" + pformat(distances_start, width=240))
    logging.debug("\n" + pformat(distances_end, width=240))

    logging.info(f"Closest possible start {distances_start[0][1]:.2f} km")
    logging.info(f"Closest possible end {distances_end[0][1]:.2f} km")
    return distances_start, distances_end


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
