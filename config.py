# STORAGE
ALWAYS_GRAPH = False  # Always re-create the graph
ALWAYS_PARSE = False  # Always re-create cached segments dicts
ALWAYS_REDUCE = False  # Always re-create reduced gpx files

# DISPLAY
SCALE_FACTOR = 20  # How "big" the map is, the larger the more downsacling takes place.

# COMMON
REDUCTION_DISTANCE = 1000.0  # in meter
ROUTES_FOUND_END = 1  # Max number of requested routes

# GRAPH
GRAPH_CONNECTION_DISTANCE = 5  # In km, When a point to another point is considered connected
PRECISION = 10  # Every nth point is part of the graph

# OLD APPROACH
COUNTRY = "at"
GPX_FILE_PATTERN = "*.gpx"  # Glob pattern
MAX_DETOUR = 5  # in km
MAX_END_DISTANCE = 10.0  # in km
MIN_GAP_DIS = 5.0  # in km
POINTS_ITERATOR_GAP = 10  # in km
