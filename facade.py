import argparse
import logging
import math
import os
import statistics
import sys
import time
import webbrowser
from collections import defaultdict
from posixpath import split
from pprint import pprint

import build_graph
import build_segments
import config
import display
import distance
import gpx2ascii
import gpx_tools
import utils


def load_worldcities():
    """From https://simplemaps.com/data/world-cities"""
    cities = defaultdict(list)
    with open(os.path.join("data", "worldcities.csv"), encoding="utf8") as f:
        lines = f.readlines()
    # Skip the first one which is a string
    for line in lines[1:]:
        split = line.split('","')
        city = split[1].strip().replace('"', "").lower()
        lat = float(split[2].strip().replace('"', ""))
        lon = float(split[3].strip().replace('"', ""))
        cities[city].append((lat, lon))
    return cities


def find_start_and_end(cities, start_city, end_city):
    if start_city.lower() not in cities.keys():
        logging.error(f"{start_city} not found, exiting.")
        sys.exit(1)

    if end_city.lower() not in cities.keys():
        logging.error(f"{end_city} not found, exiting.")
        sys.exit(1)

    possible_starts = cities[start_city.lower()]
    possible_ends = cities[end_city.lower()]

    logging.info(f"Number of possible start cities: {len(possible_starts)}.")
    logging.info(f"Number of possible end cities: {len(possible_ends)}.")

    min_dis = math.inf
    selected_start = None
    selected_end = None
    for possible_start in possible_starts:
        for possible_end in possible_ends:
            dis = distance.haversine(possible_start, possible_end)
            if dis < min_dis:
                min_dis = dis
                selected_start = possible_start
                selected_end = possible_end

    return selected_start, selected_end


def parse_args():
    parser = argparse.ArgumentParser(description="GPX Path.")
    parser.add_argument("--start", required=True, help="Start City")
    parser.add_argument("--end", required=True, help="End City")
    parser.add_argument("--gpx", required=True, help="Relative Path to GPX Data Source")
    parser.add_argument("--silent", action="store_true", help="Do not do any extra stuff")
    args = parser.parse_args()
    return args


def load_background():
    germany_gpx_path = os.path.join("maps", "1000_germany.gpx")
    germany_points = gpx2ascii.load_all_points(germany_gpx_path)
    switzerland_gpx_path = os.path.join("maps", "1000_switzerland.gpx")
    switzerland_points = gpx2ascii.load_all_points(switzerland_gpx_path)
    austria_gpx_path = os.path.join("maps", "1000_austria.gpx")
    austria_points = gpx2ascii.load_all_points(austria_gpx_path)
    return germany_points + switzerland_points + austria_points


def print_important_infos():
    logging.info(f"Starting")
    if config.ALWAYS_REDUCE:
        logging.warning("Option config.ALWAYS_REDUCE is active.")
    if config.ALWAYS_PARSE:
        logging.warning("Option config.ALWAYS_PARSE is active.")
    if config.ALWAYS_GRAPH:
        logging.warning("Option config.ALWAYS_GRAPH is active.")

    logging.info(f"Using graph version '{config.GRAPH_MODUL.__name__}'.")
    logging.info(
        f"Minimum possible distance between points: {config.REDUCTION_DISTANCE * config.PRECISION / 1000:.2f} km."
    )


def load_segments(gpx_path):
    pickle_file_name = "_".join(
        [str(int(config.REDUCTION_DISTANCE)), utils.replace_os_separator(gpx_path), "segments.p"]
    )

    pickle_path = os.path.join(config.STORAGE_TEMP_DIR, "segments", pickle_file_name)
    logging.info(f"Storage path: {pickle_path}.")

    glob_search_pattern = os.path.join(gpx_path, "*.gpx")
    logging.info(f"Glob search pattern: {glob_search_pattern}.")

    segments_dict = build_segments.build_segments_dict(
        config.REDUCTION_DISTANCE, pickle_path, glob_search_pattern, config.STORAGE_TEMP_DIR
    )
    return segments_dict


def load_map(segments_dict, gpx_path):
    map_file_name = "_".join(
        [
            str(int(config.REDUCTION_DISTANCE)),
            utils.replace_os_separator(gpx_path),
            str(int(config.GRAPH_CONNECTION_DISTANCE)),
            str(int(config.PRECISION)),
            str(int(config.COST_SWITCH_SEGMENT_PENALTY)),
            str(config.GRAPH_MODUL.__name__),
            "map.p",
        ]
    )
    map = build_graph.load_or_build_map(segments_dict, map_file_name, os.path.join(config.STORAGE_TEMP_DIR, "maps"))

    if not len(map.keys()):
        logging.error(f"No keys in map, exiting.")
        sys.exit(1)
    return map


def perform_dijksra(start_gps, end_gps, segments_dict, background, map):
    logging.info("Finding dijkstra path...")
    start_time = time.time()
    dijkstra = build_graph.find_path(map, start_gps, end_gps, map.dijkstra)
    rescaled_dijkstra = build_graph.rescale(segments_dict, dijkstra)
    logging.info(f"Elapsed time {time.time() - start_time:.2f} s.")

    build_graph.create_and_display_map(dijkstra, "Dijkstra path", background)

    gpx_tools.save_as_gpx_file(dijkstra, config.RESULTS_FOLDER, "dijkstra.gpx")
    gpx_tools.save_as_gpx_file(rescaled_dijkstra, config.RESULTS_FOLDER, "dijkstra_rescaled.gpx")
    display.save_gpx_as_html("dijkstra", config.RESULTS_FOLDER)
    display.save_gpx_as_html("dijkstra_rescaled", config.RESULTS_FOLDER)


def perform_shortest(start_gps, end_gps, segments_dict, background, map):
    logging.info("Finding shortest path...")
    start_time = time.time()
    shortest = build_graph.find_path(map, start_gps, end_gps, map.find_shortest_path)
    rescaled_shortest = build_graph.rescale(segments_dict, shortest)
    logging.info(f"Elapsed time {time.time() - start_time:.2f} s.")

    build_graph.create_and_display_map(shortest, "Shortest path", background)

    gpx_tools.save_as_gpx_file(shortest, config.RESULTS_FOLDER, "shortest.gpx")
    gpx_tools.save_as_gpx_file(rescaled_shortest, config.RESULTS_FOLDER, "shortest_rescaled.gpx")
    display.save_gpx_as_html("shortest", config.RESULTS_FOLDER)
    display.save_gpx_as_html("shortest_rescaled", config.RESULTS_FOLDER)


def main():
    print_important_infos()

    args = parse_args()
    cities = load_worldcities()
    logging.info(f"Loaded {len(cities)} cities.")

    start_gps, end_gps = find_start_and_end(cities, args.start, args.end)
    logging.info(f"Start GPS for {args.start}: {start_gps}.")
    logging.info(f"End GPS for {args.end}: {end_gps}.")

    segments_dict = load_segments(args.gpx)

    all_points = build_graph.collect_all_points(segments_dict)
    logging.info(f"Number of points in segments {str(len(all_points))}.")

    background = load_background()

    build_graph.create_and_display_map(all_points, "All Points", background)

    map = load_map(segments_dict, args.gpx)

    logging.info(f"Building a heuristic.")
    map.build_heuristic(gpx_tools.SimplePoint(end_gps))

    logging.info(f"Number of keys in graph {str(len(map.keys()))}.")
    logging.info(f"Number of total nodes in graph {str(len(map.nodes()))}.")
    logging.info(f"Quantiles weights {str(statistics.quantiles(map.weights(), n=10))}.")

    # TODO Consider removing this
    # TODO perform_shortest(start_gps, end_gps, segments_dict, background, map)
    perform_dijksra(start_gps, end_gps, segments_dict, background, map)

    if not args.silent:
        webbrowser.open_new_tab(os.path.join(config.RESULTS_FOLDER, "shortest.html"))
        webbrowser.open_new_tab(os.path.join(config.RESULTS_FOLDER, "shortest_rescaled.html"))
        webbrowser.open_new_tab(os.path.join(config.RESULTS_FOLDER, "dijkstra.html"))
        webbrowser.open_new_tab(os.path.join(config.RESULTS_FOLDER, "dijkstra_rescaled.html"))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s:%(msecs)03d %(levelname)s: %(message)s", datefmt="%H:%M:%S"
    )
    main()
