import os
import astar
import graph

# STORAGE
ALWAYS_GRAPH = False  # Always re-create the graph
ALWAYS_PARSE = False  # Always re-create cached segments dicts
ALWAYS_REDUCE = False  # Always re-create reduced gpx files

# DIRECTORIES
STORAGE_TEMP_DIR = "tmp"
RESULTS_FOLDER = "results"

# USER INPUTS
GPX_PATH = os.path.join("adfc")
START_GPS, END_GPS = (46.3695817,6.006102), (54.5237462,13.4666073)

# DISPLAY
SCALE_FACTOR = 40  # How "big" the map is, the larger the more downsacling takes place.

# COMMON
REDUCTION_DISTANCE = 1000.0  # The distance betwen two GPS points during reduction phase, in meter.

# GRAPH
GRAPH_CONNECTION_DISTANCE = 5.0  # In km, When a point to another point is considered connected.
PRECISION = 1  # Every nth point is part of the graph or evaluated as a adjacent point.
COST_NORMAL_PENALTY = 1  # Cost for normal next points.
COST_SWITCH_SEGMENT_PENALTY = 50000 / REDUCTION_DISTANCE  # Cost for switching segments.
PRECISION_OTHER_SEGMENT = (
    100  # Every nth point is part of the graph or evaluated as a adjacent point on other segments.
)

# DEBUG
USE_SMART_ALGO = True
GRAPH_MODUL = astar
