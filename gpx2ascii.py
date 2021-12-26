import copy
import glob
import math
from pprint import pformat
import os
import gpxpy

import config
import distance


def determine_index(point, edges):
    distance_w = distance.haversine((edges[1][1][0], point[1]), point)
    distance_h = distance.haversine((point[0], edges[1][1][1]), point)
    w, h = int(distance_w / config.SCALE_FACTOR), int(distance_h / config.SCALE_FACTOR)
    return w, h


def determine_bounding_box(map):
    min_lat, min_lon = math.inf, math.inf
    max_lat, max_lon = 0, 0
    edges = [[0 for x in range(2)] for y in range(2)]
    for track in map.tracks:
        for segment in track.segments:
            for point in segment.points:
                max_lat = max(max_lat, point.latitude)
                max_lon = max(max_lon, point.longitude)
                min_lat = min(min_lat, point.latitude)
                min_lon = min(min_lon, point.longitude)

    print(f"Bounding box: MIN_LAT: {min_lat}, MIN_LON:{min_lon}, MAX_LA:{max_lat}, MAX_LON{max_lon}")

    edges[0][0] = (max_lat, min_lon)  # top left
    edges[0][1] = (max_lat, max_lon)  # top right
    edges[1][0] = (min_lat, max_lon)  # bottom right
    edges[1][1] = (min_lat, min_lon)  # bottom left
    return edges


def create_map(file_name, map=None, character="x"):
    with open(file_name, "r") as f:
        gpx = gpxpy.parse(f)

    _, edges = default_bounding_box()
    if not map:
        map, edges = default_bounding_box()

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points[:: config.SCALE_FACTOR]:
                idx_w, idx_h = determine_index((point.latitude, point.longitude), edges)
                map[idx_w][idx_h] = character

    return map


def default_bounding_box():
    # Set Germany as boundaries
    bottom_left = (47.2, 5.8)
    top_right = (54.9, 15.1)
    bottom_right = (bottom_left[0], top_right[1])
    top_left = (top_right[0], bottom_left[1])

    distance_w = distance.haversine(bottom_left, bottom_right)
    distance_h = distance.haversine(bottom_left, top_left)
    w, h = int(distance_w / config.SCALE_FACTOR + 1), int(distance_h / config.SCALE_FACTOR + 1)
    map = [[" " for x in range(w)] for y in range(h)]

    edges = [[0 for x in range(2)] for y in range(2)]
    edges[0][0] = top_left
    edges[0][1] = top_right
    edges[1][0] = bottom_right
    edges[1][1] = bottom_left
    return map, edges


def print_edges(bottom_left, top_right, bottom_right, top_left, edges, map):
    print(f"Edges: {pformat(edges)}")
    w, h = determine_index(top_left, edges)
    map[w][h] = "TL"
    w, h = determine_index(top_right, edges)
    map[w][h] = "TR"
    w, h = determine_index(bottom_right, edges)
    map[w][h] = "BR"
    w, h = determine_index(bottom_left, edges)
    map[w][h] = "BL"


def display(map):
    display_string = ""
    for lines in reversed(map):
        for line in lines:
            display_string += str(f"{line} ")
        display_string += "\n"

    print()
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


if __name__ == "__main__":
    track_file_names = glob.glob(os.path.join("bikeline", "de", config.GPX_FILE_PATTERN))
    track_file_names = glob.glob(os.path.join("adfc", "", config.GPX_FILE_PATTERN))

    germany = create_map(os.path.join("germany", "1000_germany.gpx"), None, ".")
    display(germany)

    for track in track_file_names:
        if not "Koenigssee" in track:
            continue

        print(track)
        map = create_map(track, copy.deepcopy(germany))
        display(map)
