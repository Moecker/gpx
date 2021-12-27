import logging
import os

import build_graph
import build_segments
import config
import display
import gpx2ascii
import gpx_tools
import utils


def with_background():
    germany_gpx_path = os.path.join("maps", "1000_germany.gpx")
    germany_points = gpx2ascii.load_all_points(germany_gpx_path)
    switzerland_gpx_path = os.path.join("maps", "1000_switzerland.gpx")
    switzerland_points = gpx2ascii.load_all_points(switzerland_gpx_path)
    austria_gpx_path = os.path.join("maps", "1000_austria.gpx")
    austria_points = gpx2ascii.load_all_points(austria_gpx_path)
    return germany_points + switzerland_points + austria_points


def main():
    pickle_file_name = "_".join(
        [str(int(config.REDUCTION_DISTANCE)), utils.replace_os_seperator(config.GPX_PATH), "segments.p"]
    )

    pickle_path = os.path.join(config.STORAGE_TEMP_DIR, "segments", pickle_file_name)
    logging.info(f"Storage path: {pickle_path}.")

    glob_search_pattern = os.path.join(config.GPX_PATH, "*.gpx")
    logging.info(f"Glob search pattern: {glob_search_pattern}.")

    segments_dict = build_segments.build_segments_dict(
        config.REDUCTION_DISTANCE, pickle_path, glob_search_pattern, config.STORAGE_TEMP_DIR
    )

    background = with_background()

    all_points = build_graph.collect_all_points(segments_dict)
    build_graph.create_and_display_map(all_points, "All Points", background)

    logging.info(f"Number of points in segments {str(len(all_points))}.")

    map_file_name = "_".join(
        [
            str(int(config.REDUCTION_DISTANCE)),
            utils.replace_os_seperator(config.GPX_PATH),
            str(int(config.GRAPH_CONNECTION_DISTANCE)),
            str(int(config.PRECISION)),
            "map.p",
        ]
    )
    map = build_graph.load_or_build_map(segments_dict, map_file_name, os.path.join(config.STORAGE_TEMP_DIR, "maps"))

    logging.info(f"Number of nodes in graph {str(len(map._graph.values()))}.")

    logging.info("Finding shortest path.")
    shortest = build_graph.find_path(map, config.START_GPS, config.END_GPS, map.find_shortest_path)

    build_graph.create_and_display_map(shortest, "Shortest path", background)

    gpx_tools.save_as_gpx_file(all_points, config.RESULTS_FOLDER, "all_points.gpx")
    gpx_tools.save_as_gpx_file(shortest, config.RESULTS_FOLDER, "shortest_path.gpx")

    display.save_gpx_as_html("all_points", config.RESULTS_FOLDER)
    display.save_gpx_as_html("shortest_path", config.RESULTS_FOLDER)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
