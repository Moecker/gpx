# STORAGE
ALWAYS_PARSE = False
ALWAYS_REDUCE = False

# COMMON
ROUTES_FOUND_END = 1  # Max number of requested routes
REDUCTION_DISTANCE = 100.0  # in meter

# DISPLAY
SCALE_FACTOR = 25  # How "big" the map is, the larger the more downsacling takes place.

# GRAPH
GRAPH_CONNECTION_DISTANCE = 5  # When a point to another point is considered connected
PRECISION = 10  # Every nth point is part of the graph

# OLD APPROACH
GPX_FILE_PATTERN = "*.gpx"  # Glob pattern
COUNTRY = "at"
POINTS_ITERATOR_GAP = 10  # in km
MAX_DETOUR = 5  # in km
MIN_GAP_DIS = 5.0  # in km
MAX_END_DISTANCE = 10.0  # in km
