import logging
import os

import build_graph
import build_segments
import config
import utils

# User Inputs
GPX_PATH = os.path.join("bikeline", "ch")
START_GPS, END_GPS = (46.102391,6.14088001), (47.6971025,10.54265806)

# Internal configs
STORAGE_TEMP_DIR = "tmp"


def main():
    pickle_file_name = "_".join(
        [str(int(config.REDUCTION_DISTANCE)), utils.replace_os_seperator(GPX_PATH), "segments.p"]
    )
    pickle_path = os.path.join(STORAGE_TEMP_DIR, pickle_file_name)
    logging.info(f"Storage path: {pickle_path}.")

    glob_search_pattern = os.path.join(GPX_PATH, "*.gpx")
    logging.info(f"Glob search pattern: {glob_search_pattern}.")
    segments_dict = build_segments.build_segments_dict(
        config.REDUCTION_DISTANCE, pickle_path, glob_search_pattern, STORAGE_TEMP_DIR
    )

    all_points = build_graph.get_all_points(segments_dict)
    build_graph.create_and_display_map(all_points, "All Points")

    map_file_name = "_".join(
        [
            str(int(config.REDUCTION_DISTANCE)),
            str(int(config.GRAPH_CONNECTION_DISTANCE)),
            str(int(config.PRECISION)),
            "map.p",
        ]
    )
    map = build_graph.load_or_build_map(segments_dict, map_file_name, STORAGE_TEMP_DIR)

    logging.info("Finding random path")
    random_path = build_graph.find_path(map, START_GPS, END_GPS, map.find_path)
    build_graph.create_and_display_map(random_path, "Random Path")

    logging.info("Finding shortest path")
    shortest = build_graph.find_path(map, START_GPS, END_GPS, map.find_shortest_path)
    build_graph.create_and_display_map(shortest, "Shortest Path")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
