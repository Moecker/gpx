import gpxpy
from pprint import pformat
import distance
import glob
import config
import os
import reducer
import copy

RESOLUTION = 20


def determine_index(point, edges):
    distance_w = distance.haversine((edges[1][1][0], point[1]), point)
    distance_h = distance.haversine((point[0], edges[1][1][1]), point)
    w, h = int(distance_w / RESOLUTION), int(distance_h / RESOLUTION)
    return w, h


def create_map(file_name, map=None, character="x"):
    bottom_left = (47.2, 5.8)
    top_right = (54.9, 15.1)
    bottom_right = (bottom_left[0], top_right[1])
    top_left = (top_right[0], bottom_left[1])

    edges = [[0 for x in range(2)] for y in range(2)]
    edges[0][0] = top_left
    edges[0][1] = top_right
    edges[1][0] = bottom_right
    edges[1][1] = bottom_left

    distance_w = distance.haversine(bottom_left, bottom_right)
    distance_h = distance.haversine(bottom_left, top_left)
    w, h = int(distance_w / RESOLUTION + 1), int(distance_h / RESOLUTION + 1)
    
    if not map:
        map = [[" " for x in range(w)] for y in range(h)]

    with open(file_name, "r") as f:
        gpx = gpxpy.parse(f)

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points[::RESOLUTION]:
                idx_w, idx_h = determine_index((point.latitude, point.longitude), edges)
                map[idx_w][idx_h] = character

    return map


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
    print(display_string)


if __name__ == "__main__":
    track_file_names = glob.glob(os.path.join("bikeline", "de", config.GPX_FILE_PATTERN))
    track_file_names = glob.glob(os.path.join("adfc", "", config.GPX_FILE_PATTERN))

    germany = create_map(os.path.join("germany", "1000_germany.gpx"), None, ".")
    display(germany)

    for track in track_file_names:
        print(track)
        # map = create_map(track, copy.deepcopy(germany))
        map = create_map(track, germany)
        display(map)
