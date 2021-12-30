from collections import defaultdict
from pickle import FALSE
from posixpath import split
from pprint import pprint
import argparse
import build_graph
import build_segments
import config
import display
import distance
import gpx_display
import gpx_tools
import logging
import math
import os
import statistics
import sys
import time
import utils
import webbrowser


def annotate_points(segments_dict):
    for name, segment in segments_dict.items():
        for idx, point in enumerate(segment.points):
            gpx_tools.annotate(point, name, idx)


def check_city(cities, city):
    if city.lower() not in cities.keys():
        logging.warning(f"City '{city}' not found, try again.")
        return False
    return True


def open_web_browser():
    file_path = os.path.join(config.RESULTS_FOLDER, "dijkstra_rescaled.html")
    if sys.platform == "darwin":
        file_path = "file:///" + os.path.join(os.getcwd(), file_path)
    webbrowser.open_new_tab(file_path)


def find_start_and_end(cities, start_city, end_city):
    found_start = check_city(cities, start_city)
    found_end = check_city(cities, end_city)

    if not found_start or not found_end:
        logging.error(f"Start and/or End city not found.")
        return none_tuple()

    possible_starts = cities[start_city.lower()]
    possible_ends = cities[end_city.lower()]

    logging.debug(f"Number of possible start cities: {len(possible_starts)}.")
    logging.debug(f"Number of possible end cities: {len(possible_ends)}.")

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


def interactive_mode(cities, segments_dict, background, map, dry):
    try:
        while True:
            logging.info(f"Input the start and end city. Leave blank or hit CTRL+C to exit.")
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
            perform_run(cities, start_city, end_city, segments_dict, background, map, dry)
    except (KeyboardInterrupt):
        sys.exit(0)


def load_background():
    germany_gpx_path = os.path.join("maps", "1000_germany.gpx")
    germany_points = gpx_display.load_all_points(germany_gpx_path)
    switzerland_gpx_path = os.path.join("maps", "1000_switzerland.gpx")
    switzerland_points = gpx_display.load_all_points(switzerland_gpx_path)
    austria_gpx_path = os.path.join("maps", "1000_austria.gpx")
    austria_points = gpx_display.load_all_points(austria_gpx_path)
    return germany_points + switzerland_points + austria_points


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
        logging.error(f"No keys in map.")
        return None
    return map


def load_segments(gpx_path):
    pickle_file_name = "_".join(
        [str(int(config.REDUCTION_DISTANCE)), utils.replace_os_separator(gpx_path), "segments.p"]
    )

    pickle_path = os.path.join(config.STORAGE_TEMP_DIR, "segments", pickle_file_name)
    logging.debug(f"Storage path: '{utils.make_path_clickable(pickle_path)}'.")

    glob_search_pattern = os.path.join(gpx_path, "*.gpx")
    logging.debug(f"Glob search pattern: '{glob_search_pattern}'.")

    segments_dict = build_segments.build_segments_dict(
        config.REDUCTION_DISTANCE, pickle_path, glob_search_pattern, config.STORAGE_TEMP_DIR
    )
    return segments_dict


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


def main(args):
    for _ in logging.root.manager.loggerDict:
        logging.getLogger(_).setLevel(logging.CRITICAL)

    utils.add_logging_level("TRACE", 1)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s:%(msecs)03d %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.interactive and (args.start or args.end):
        logging.warning(f"Arguments --start and --end are ignored in interactive mode.")

    print_important_infos()

    cities = load_worldcities()
    logging.debug(f"Loaded {len(cities)} cities.")

    segments_dict = load_segments(args.gpx)
    if not segments_dict:
        logging.error("Error loading segments.")
        sys.exit(1)

    annotate_points(segments_dict)

    all_points = build_graph.collect_all_points(segments_dict)
    logging.debug(f"Number of points in segments {str(len(all_points))}.")

    if not args.dry:
        gpx_tools.save_as_gpx_file(all_points, config.RESULTS_FOLDER, "all_points.gpx")
        display.save_gpx_as_html("all_points", config.RESULTS_FOLDER)

    background = load_background()

    gpx_display.create_and_display_map(all_points, "Map of all points in database", background)

    map = load_map(segments_dict, args.gpx)
    build_graph.adjust_weight_foreign_segments(map)

    dijkstra_rescaled = None
    if args.interactive:
        interactive_mode(cities, segments_dict, background, map, args.dry)
    else:
        dijkstra_rescaled = normal_mode(args, cities, segments_dict, background, map, args.dry)
    return dijkstra_rescaled


def normal_mode(args, cities, segments_dict, background, map, dry):
    loop = 0
    while True:
        if loop >= config.NUMBER_OF_PATHS:
            logging.info(f"Maximum configured number of {config.NUMBER_OF_PATHS} path(s) found.")
            break

        loop += 1
        logging.info(f"Searching path {loop} of {config.NUMBER_OF_PATHS}.")
        dijkstra, dijkstra_rescaled = perform_run(cities, args.start, args.end, segments_dict, background, map, dry)

        if not dijkstra or not dijkstra_rescaled:
            break

        build_graph.adjust_weight_of_path(dijkstra, map)
        continue
    return dijkstra_rescaled


def none_tuple():
    return None, None


def parse_args():
    parser = argparse.ArgumentParser(description="GPX Path Planner.")

    parser.add_argument("--start", help="Start City", default=None)
    parser.add_argument("--end", help="End City", default=None)
    parser.add_argument("--gpx", required=True, help="Relative Path to GPX Data Source")
    parser.add_argument("--verbose", action="store_true", help="Do not do any extra stuff")
    parser.add_argument("--interactive", action="store_true", help="Interactively make multiple queries")
    parser.add_argument("--dry", action="store_true", help="Do not create any outputs")

    args = parser.parse_args()

    if not args.interactive and (args.start is None or args.end is None):
        parser.error("Arguments --start and --end are required in non interactive mode (--interactive).")
        sys.exit(1)
    return args


def perform_dijksra(start_gps, end_gps, segments_dict, background, map):
    logging.debug("Finding dijkstra path.")
    start_time = time.time()
    dijkstra = build_graph.find_path(map, start_gps, end_gps, map.dijkstra)

    if not dijkstra:
        return none_tuple()

    dijkstra_rescaled = build_graph.rescale(segments_dict, dijkstra)
    logging.info(f"Elapsed time {time.time() - start_time:.2f} s.")

    if not dijkstra_rescaled:
        return none_tuple()

    gpx_display.create_and_display_map(dijkstra, "Map of found path", background)
    gpx_display.create_and_display_map(dijkstra_rescaled, "Map of found path, rescaled", background)

    return dijkstra, dijkstra_rescaled


def perform_run(cities, start_city, end_city, segments_dict, background, map, dry):
    start_gps, end_gps = find_start_and_end(cities, start_city, end_city)

    if not start_gps or not end_gps:
        return none_tuple()

    logging.info(f"Start GPS for {start_city}: {start_gps}.")
    logging.info(f"End GPS for {end_city}: {end_gps}.")

    logging.debug(f"Building a heuristic.")
    map.build_heuristic(end_gps)

    logging.debug(f"Number of keys in graph {str(len(map.keys()))}.")
    logging.debug(f"Number of total nodes in graph {str(len(map.nodes()))}.")
    logging.debug(f"Quantiles weights {str(statistics.quantiles(map.weights(), n=10))}.")

    dijkstra, dijkstra_rescaled = perform_dijksra(start_gps, end_gps, segments_dict, background, map)

    if not dry:
        gpx_tools.save_as_gpx_file(dijkstra, config.RESULTS_FOLDER, "dijkstra.gpx")
        gpx_tools.save_as_gpx_file(dijkstra_rescaled, config.RESULTS_FOLDER, "dijkstra_rescaled.gpx")
        display.save_gpx_as_html("dijkstra", config.RESULTS_FOLDER)
        display.save_gpx_as_html("dijkstra_rescaled", config.RESULTS_FOLDER)

    return dijkstra, dijkstra_rescaled


def print_important_infos():
    if config.ALWAYS_REDUCE:
        logging.warning("Option config.ALWAYS_REDUCE is active.")
    if config.ALWAYS_PARSE:
        logging.warning("Option config.ALWAYS_PARSE is active.")
    if config.ALWAYS_GRAPH:
        logging.warning("Option config.ALWAYS_GRAPH is active.")

    logging.debug(f"Using graph version '{config.GRAPH_MODUL.__name__}'.")
    logging.debug(
        f"Minimum possible distance between points: {config.REDUCTION_DISTANCE * config.PRECISION / 1000:.2f} km."
    )
    logging.debug(f"Using cost for segment changes: {config.COST_SWITCH_SEGMENT_PENALTY}.")


if __name__ == "__main__":
    args = parse_args()
    main(args)
