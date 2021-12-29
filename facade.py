import argparse
import logging
import math
import os
from pickle import FALSE
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


def check_city(cities, city):
    if city.lower() not in cities.keys():
        logging.warning(f"{city} not found.")
        return False
    return True


def find_start_and_end(cities, start_city, end_city):
    found_start = check_city(cities, start_city)
    found_end = check_city(cities, end_city)

    if not found_start or not found_end:
        logging.error(f"Start and/or End city not found, returning.")
        return None, None

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

    return gpx_tools.SimplePoint(selected_start), gpx_tools.SimplePoint(selected_end)


def load_background():
    germany_gpx_path = os.path.join("maps", "1000_germany.gpx")
    germany_points = gpx2ascii.load_all_points(germany_gpx_path)
    switzerland_gpx_path = os.path.join("maps", "1000_switzerland.gpx")
    switzerland_points = gpx2ascii.load_all_points(switzerland_gpx_path)
    austria_gpx_path = os.path.join("maps", "1000_austria.gpx")
    austria_points = gpx2ascii.load_all_points(austria_gpx_path)
    return germany_points + switzerland_points + austria_points


def print_important_infos():
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
    logging.info(f"Using cost for segment changes: {config.COST_SWITCH_SEGMENT_PENALTY}.")


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
        logging.error(f"No keys in map, returning.")
        return None
    return map


def perform_dijksra(start_gps, end_gps, segments_dict, background, map):
    logging.info("Finding dijkstra path...")
    start_time = time.time()
    dijkstra = build_graph.find_path(map, start_gps, end_gps, map.dijkstra)
    dijkstra_rescaled = build_graph.rescale(segments_dict, dijkstra)
    logging.info(f"Elapsed time {time.time() - start_time:.2f} s.")

    if not dijkstra or not dijkstra_rescaled:
        return None, None

    build_graph.create_and_display_map(dijkstra, "Dijkstra path", background)

    gpx_tools.save_as_gpx_file(dijkstra, config.RESULTS_FOLDER, "dijkstra.gpx")
    gpx_tools.save_as_gpx_file(dijkstra_rescaled, config.RESULTS_FOLDER, "dijkstra_rescaled.gpx")
    display.save_gpx_as_html("dijkstra", config.RESULTS_FOLDER)
    display.save_gpx_as_html("dijkstra_rescaled", config.RESULTS_FOLDER)

    return dijkstra, dijkstra_rescaled


def do_additional_stuff():
    file_path = os.path.join(config.RESULTS_FOLDER, "dijkstra_rescaled.html")
    if sys.platform == "darwin":
        file_path = "file:///" + os.path.join(os.getcwd(), file_path)
    webbrowser.open_new_tab(file_path)


def perform_run(cities, start_city, end_city, segments_dict, background, map, silent):
    start_gps, end_gps = find_start_and_end(cities, start_city, end_city)
    if not start_gps or not end_gps:
        return False

    logging.info(f"Start GPS for {start_city}: {start_gps}.")
    logging.info(f"End GPS for {end_city}: {end_gps}.")

    logging.info(f"Building a heuristic.")
    map.build_heuristic(end_gps)

    logging.info(f"Number of keys in graph {str(len(map.keys()))}.")
    logging.info(f"Number of total nodes in graph {str(len(map.nodes()))}.")
    logging.info(f"Quantiles weights {str(statistics.quantiles(map.weights(), n=10))}.")

    dijkstra, dijkstra_rescaled = perform_dijksra(start_gps, end_gps, segments_dict, background, map)

    if not silent:
        do_additional_stuff()

    return dijkstra, dijkstra_rescaled


def interactive_mode(cities, segments_dict, background, map, silent):
    try:
        while True:
            logging.info(f"Input the start/end city. Leave blank to exit.")
            while True:
                start_city = input("Origin: ")
                if start_city == "":
                    sys.exit(0)
                if not check_city(cities, start_city):
                    continue
                break
            while True:
                end_city = input("Destination: ")
                if end_city == "":
                    sys.exit(0)
                if not check_city(cities, end_city):
                    continue
                break
            perform_run(cities, start_city, end_city, segments_dict, background, map, silent)
    except (KeyboardInterrupt):
        sys.exit(0)


def annotate_points(segments_dict):
    for name, segment in segments_dict.items():
        for idx, point in enumerate(segment.points):
            build_graph.annotate(point, name, idx)


def main():
    logging.info(f"Starting...")

    args = parse_args()

    print_important_infos()

    cities = load_worldcities()
    logging.info(f"Loaded {len(cities)} cities.")

    segments_dict = load_segments(args.gpx)
    annotate_points(segments_dict)

    all_points = build_graph.collect_all_points(segments_dict)
    logging.info(f"Number of points in segments {str(len(all_points))}.")

    background = load_background()

    build_graph.create_and_display_map(all_points, "All Points", background)

    map = load_map(segments_dict, args.gpx)

    if args.interactive:
        interactive_mode(cities, segments_dict, background, map, args.silent)
    else:
        while True:
            dijkstra, dijkstra_rescaled = perform_run(
                cities, args.start, args.end, segments_dict, background, map, args.silent
            )
            if dijkstra and dijkstra_rescaled:
                build_graph.adjust_weight_of_path(dijkstra, map)
                logging.info("Waiting for next run...")
                time.sleep(0.1)
            else:
                break


def parse_args():
    parser = argparse.ArgumentParser(description="GPX Path.")
    parser.add_argument("--start", help="Start City", default=None)
    parser.add_argument("--end", help="End City", default=None)
    parser.add_argument("--gpx", required=True, help="Relative Path to GPX Data Source")
    parser.add_argument("--silent", action="store_true", help="Do not do any extra stuff")
    parser.add_argument("--interactive", action="store_true", help="Interactively make multiple queries")
    args = parser.parse_args()

    if not args.interactive and (args.start is None or args.end is None):
        parser.error("Arguments --start and --end are required in non interactive mode (--interactive).")
    if args.interactive and (args.start or args.end):
        logging.warning(f"Arguments --start and --end are ignored in interactive mode.")
    return args


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s:%(msecs)03d %(levelname)s: %(message)s", datefmt="%H:%M:%S"
    )
    main()
