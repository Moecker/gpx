import astar
import graph

# Controls whether to always re-create the graph.
ALWAYS_GRAPH = False

# Controls whether to always re-create cached segments dicts.
ALWAYS_PARSE = False

# Controls whether to always re-create reduced gpx files.
ALWAYS_REDUCE = False

# Location for intermediate results, such as maps and segments for caching.
STORAGE_TEMP_DIR = "tmp"

# Location for the final results, GPX track files and HTML map views.
RESULTS_FOLDER = "results"

# How "big" the map is as ASCI art output, the larger the more downsacling takes place.
SCALE_FACTOR = 40

# The distance betwen two GPS points during reduction phase, in meter.
# This determines the minimal possible distance which can be later represented as a GPX track.
REDUCTION_DISTANCE = 100.0

# Every nth point is part of the graph or evaluated as an adjacent point.
# If increased, some points are skipped during evaluation of distances to other points,
# but they are also ignored and not part of the actual graph.
PRECISION = 20

# The maximum distance when a point to another point is considered connected, in km.
# A lower value means that there are more connections in the graph, that is, there could be
# a connection from Hamburg to Berlin with a big cost, however keeping this value in a good range
# is a trade off between not being able to connect other segments vs. a too huge graph.
GRAPH_CONNECTION_DISTANCE = 2.0

# Cost for points which are next to each other within a segment.
COST_NORMAL_PENALTY = 1

# Cost for switching segments to avoid jumping around similar segments.
COST_SWITCH_SEGMENT_PENALTY = 500

# A factor applied to the heuristic of A-Star which helps finding
# the shortest path to other nodes quicker.
HEURISTIC_SCALE_FACTOR = 100

# The used module which implements the graph.
GRAPH_MODUL = astar
