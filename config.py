import os

# STORAGE
ALWAYS_GRAPH = False  # Always re-create the graph
ALWAYS_PARSE = False  # Always re-create cached segments dicts
ALWAYS_REDUCE = False  # Always re-create reduced gpx files

# DIRECTORIES
STORAGE_TEMP_DIR = "tmp"
RESULTS_FOLDER = "results"

# USER INPUTS
GPX_PATH = os.path.join("bikeline", "ch")
GPX_PATH = os.path.join("adfc")
START_GPS, END_GPS = (48.2, 11.4), (51.1, 6.4)


# DISPLAY
SCALE_FACTOR = 20  # How "big" the map is, the larger the more downsacling takes place.

# COMMON
REDUCTION_DISTANCE = 500.0  # The distance betwen two GPS points during reduction phase, in meter.

# GRAPH
GRAPH_CONNECTION_DISTANCE = 10.0  # In km, When a point to another point is considered connected.
PRECISION = 10  # Every nth point is part of the graph or evaluated as a adjacent point.
