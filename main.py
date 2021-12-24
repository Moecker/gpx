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


def determine_start():
    munich_gps = gpxpy.gpx.GPXTrackPoint(48.13743, 11.57549)
    return munich_gps


def determine_reduction_threshold():
    return 500.0


def try_load_pickle(pickle_path):
    if os.path.isfile(pickle_path):
        logging.info(f"{pickle_path} exists, using it.")
        gpxs = pickle.load(open(pickle_path, "rb"))
        return gpxs
    else:
        return None


def compute_distances(start_gps, gpxs):
    distances = dict()
    for name, gpx in gpxs.items():
        min_distance = math.inf
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    dis = distance.haversine_gpx(point, start_gps)
                    if dis < min_distance:
                        min_distance = dis
        logging.debug(f"Minimum Distance: {min_distance:.2f} km")
        distances[name] = min_distance
    return distances


def load_and_reduce_gpxs(track_file_names, threshold, pickle_path):
    logging.warning(f"{pickle_path} does not exist, creating it.")

    gpxs = dict()
    for track_file_name in track_file_names:
        threshold_string = str(int(threshold))
        track_file_name_reduced = os.path.join(
            "output", threshold_string, threshold_string + "_" + track_file_name.replace("/", "_")
        )

        if not os.path.isfile(track_file_name_reduced):
            logging.warning(f"{track_file_name_reduced} does not exist, creating it.")
            try:
                reducer.reduce(track_file_name, threshold, track_file_name_reduced)
            except:
                logging.error(f"Error while reducing {track_file_name} to create {track_file_name_reduced}")
                continue
        else:
            logging.info(f"{track_file_name_reduced} exists, using it.")

        with open(track_file_name_reduced, "r") as f:
            gpx = gpxpy.parse(f)
            gpxs[track_file_name_reduced] = gpx
    return gpxs


def walk_gpx(gpx):
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                print(point)

def main():
    start_gps = determine_start()
    reduction_threshold = determine_reduction_threshold()

    pickle_path = os.path.join("pickle", "gpxs.p")
    gpxs = try_load_pickle(pickle_path)

    if not gpxs:
        track_file_names = glob.glob("bikeline/at/*1.gpx")
        gpxs = load_and_reduce_gpxs(track_file_names, reduction_threshold, pickle_path)
        pickle.dump(gpxs, open(pickle_path, "wb"))
    logging.info(f"Found {len(gpxs)} tracks")

    distances = compute_distances(start_gps, gpxs)
    distances = sorted(distances.items(), key=lambda x: x[1])
    logging.debug("\n" + pformat(distances))

    walk_gpx(gpxs[distances[0][0]])


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
