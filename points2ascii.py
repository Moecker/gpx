import logging
import math

import config
import distance


def determine_bounding_box(points):
    min_lat, min_lon = math.inf, math.inf
    max_lat, max_lon = 0, 0
    edges = [[0 for x in range(2)] for y in range(2)]

    for point in points:
        max_lat = max(max_lat, point.latitude)
        max_lon = max(max_lon, point.longitude)
        min_lat = min(min_lat, point.latitude)
        min_lon = min(min_lon, point.longitude)

    logging.info(f"Bounding box: ({min_lat:.2f}, {min_lon:.2f}), ({max_lat:.2f}, {max_lon:.2f}).")

    edges[0][0] = (max_lat, min_lon)  # top left
    edges[0][1] = (max_lat, max_lon)  # top right
    edges[1][0] = (min_lat, max_lon)  # bottom right
    edges[1][1] = (min_lat, min_lon)  # bottom left

    return edges


def create_map(edges, default_character):
    distance_w = distance.haversine(edges[1][1], edges[1][0])
    distance_h = distance.haversine(edges[1][1], edges[0][0])

    w, h = int(distance_w / config.SCALE_FACTOR + 1), int(distance_h / config.SCALE_FACTOR + 1)
    map = [[default_character for x in range(w)] for y in range(h)]

    return map
