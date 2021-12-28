import os

# STORAGE
ALWAYS_GRAPH = False  # Always re-create the graph.
ALWAYS_PARSE = False  # Always re-create cached segments dicts.
ALWAYS_REDUCE = False  # Always re-create reduced gpx files.

# DIRECTORIES
STORAGE_TEMP_DIR = "tmp"
RESULTS_FOLDER = "results"

# DISPLAY
SCALE_FACTOR = 40  # How "big" the map is, the larger the more downsacling takes place.

# COMMON
REDUCTION_DISTANCE = 1000.0  # The distance betwen two GPS points during reduction phase, in meter.

# GRAPH
PRECISION = 1  # Every nth point is part of the graph or evaluated as an adjacent point.
GRAPH_CONNECTION_DISTANCE = 1.0 * PRECISION  # In km, When a point to another point is considered connected.

# COSTS
COST_NORMAL_PENALTY = 1  # Cost for normal next points.
COST_SWITCH_SEGMENT_PENALTY = 10 * 1000 / REDUCTION_DISTANCE  # Cost for switching segments.
HEURISTIC_SCALE_FACTOR = 100

# ALGOS
USE_SMART_ALGO = True

# GRAPH MODUL
import astar
import graph

GRAPH_MODUL = astar
