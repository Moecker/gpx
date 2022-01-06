# Controls whether to always re-create the graph.
ALWAYS_GRAPH = False

# Controls whether to always re-create cached segments dicts.
ALWAYS_PARSE = False

# Controls whether to always re-create reduced gpx files.
ALWAYS_REDUCE = False

# Cost for points which are next to each other within a segment.
COST_NORMAL_PENALTY = 1

# Cost for switching segments to avoid jumping around similar segments.
COST_SWITCH_SEGMENT_PENALTY = 10

# Cost penalty if this node has been used before.
COST_ALREADY_VISITED_PENALTY = 100

# The maximum distance when a point to another point is considered connected, in km.
# A lower value means that there are more connections in the graph, that is, there could be
# a connection from Hamburg to Berlin with a big cost, however keeping this value in a good range
# is a trade off between not being able to connect other segments vs. a too huge graph.
# Note: Impacts Map Cache
GRAPH_CONNECTION_DISTANCE = 1

# A factor applied to the heuristic of A-Star which helps finding
# the shortest path to other nodes quicker.
HEURISTIC_SCALE_FACTOR = 10

# For test mode
IS_TEST = False

# Maximum points to export into GPX and HTML.
MAX_POINTS = 10000

# Maximum points to export overview results into GPX and HTML.
MAX_POINTS_OVERVIEW = 1000

# The number of paths to find.
NUMBER_OF_PATHS = 1

# Every nth point is part of the graph or evaluated as an adjacent point.
# If increased, some points are skipped during evaluation of distances to other points,
# but they are also ignored and not part of the actual graph.
# Note: Impacts Map Cache
PRECISION = 10

# The distance betwen two GPS points during reduction phase, in meter.
# This determines the minimal possible distance which can be later represented as a GPX track.
# Note: Impacts Reduction Cache
# Note: Impacts Segment Cache
# Note: Impacts Map Cache
REDUCTION_DISTANCE = 100

# Location for the final results, GPX track files and HTML map views.
RESULTS_FOLDER = "results"

# How "big" the map is as ASCI art output, the larger the more downsacling takes place.
SCALE_FACTOR = 50

# Location for intermediate results, such as maps and segments for caching.
STORAGE_TEMP_DIR = "tmp"

# Use the C++ binding
# Note: Impacts Segment Cache
# Note: Impacts Map Cache
USE_CPP = False

# Use python module network x.
# Note: Impacts Map Cache
USE_NETWORK_X = True

# Whether to store result in pickle files.
# If set to False, segments and maps will always be re-created.
USE_PICKLE = True

# Algorithm for building the graph.
USE_SMART = True

# Whether to use a inexact step distance to speed up the graph building process.
USE_INEXACT_STEP_DISTANCE = True


def main():
    pass
