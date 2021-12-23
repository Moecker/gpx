import gpxpy
import gpxpy.gpx
import distance
import math
import os
import reducer
import logging
from pprint import pformat
import glob

munich_gps = gpxpy.gpx.GPXTrackPoint(48.13743, 11.57549)
track_file_names = ["bikeline/de/trk00dk472.gpx", "bikeline/de/trk00fp446.gpx", "bikeline/de/trk00gu806.gpx"]

def main():
    track_file_names = glob.glob("bikeline/de/*.gpx")
    logging.info(f"Found {len(track_file_names)} tracks")

    min_dis = 1000.0
    distances = dict()
    for track_file_name in track_file_names:
        track_file_name_reduced = os.path.join("output", str(int(min_dis)) + "_" + track_file_name.replace("/", "_"))

        if not os.path.isfile(track_file_name_reduced):
            logging.warning(f"{track_file_name_reduced} does not exist, creating...")
            try:
                reducer.reduce(track_file_name, min_dis, track_file_name_reduced)
            except:
                logging.error(f"Error while reducing {track_file_name}")
                continue


        with open(track_file_name_reduced, "r") as f:
            gpx = gpxpy.parse(f)

            min_distance = math.inf
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        dis = distance.haversine_gpx(point, munich_gps)
                        if dis < min_distance:
                            min_distance = dis
            print(f"Minimum Distance: {min_distance:.2f} km")
            distances[track_file_name_reduced] = min_distance

    logging.info("\n" + pformat(sorted(distances.items(), key=lambda x: x[1])))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
