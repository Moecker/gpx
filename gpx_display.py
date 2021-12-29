from pprint import pformat
import logging
import math

import gpxpy

import config
import distance
import gpx_display


def add_waypoints(map, path, edges, character):
    assert len(map) > 0
    assert len(map[0]) > 0

    for point in path[:: config.PRECISION]:
        idx_w, idx_h = gpx_display.determine_index((point.latitude, point.longitude), edges)
        idx_w = min(idx_w, len(map) - 1)

        idx_h = min(idx_h, len(map[0]) - 1)
        map[idx_w][idx_h] = character


def create_and_display_map(path, name, background=[]):
    if not path:
        logging.warning(f"Nothing to display for '{name}', no valid points.")
        return

    logging.debug(f"Creating map '{name}'.")
    edges = determine_bounding_box(path + background)
    map = create_map(edges, " ")

    add_waypoints(map, background, edges, ".")
    add_waypoints(map, path, edges, "x")

    logging.info(f"{name}.")
    gpx_display.display(map)


def create_map(edges, default_character):
    distance_w = distance.haversine(edges[1][1], edges[1][0])
    distance_h = distance.haversine(edges[1][1], edges[0][0])

    w, h = int(distance_w / config.SCALE_FACTOR + 1), int(distance_h / config.SCALE_FACTOR + 1)
    map = [[default_character for x in range(w)] for y in range(h)]

    return map


def determine_bounding_box(points):
    min_lat, min_lon = math.inf, math.inf
    max_lat, max_lon = 0, 0
    edges = [[0 for x in range(2)] for y in range(2)]

    for point in points[:: config.PRECISION]:
        max_lat = max(max_lat, point.latitude)
        max_lon = max(max_lon, point.longitude)
        min_lat = min(min_lat, point.latitude)
        min_lon = min(min_lon, point.longitude)

    logging.debug(f"Bounding box: ({min_lat:.2f}, {min_lon:.2f}), ({max_lat:.2f}, {max_lon:.2f}).")

    edges[0][0] = (max_lat, min_lon)  # top left
    edges[0][1] = (max_lat, max_lon)  # top right
    edges[1][0] = (min_lat, max_lon)  # bottom right
    edges[1][1] = (min_lat, min_lon)  # bottom left

    return edges


def determine_index(point, edges):
    distance_w = distance.haversine((edges[1][1][0], point[1]), point)
    distance_h = distance.haversine((point[0], edges[1][1][1]), point)
    w, h = int(distance_w / config.SCALE_FACTOR), int(distance_h / config.SCALE_FACTOR)
    return w, h


def display(map):
    display_string = ""
    for lines in reversed(map):
        for line in lines:
            display_string += str(f"{line} ")
        display_string += "\n"

    print(display_string)


def load_all_points(gpx_file_name):
    with open(gpx_file_name, "r") as f:
        gpx = gpxpy.parse(f)

    all_points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                all_points.append(point)
    return all_points
