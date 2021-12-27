# TODOs
* ID1:
  * Given that segments can be very similar, we often see points "skipped" because segment1 can connect to segment2 by GRAPH_CONNECTION_DISTANCE which, in case segment1 and segment2 are very similar, can lead to "zigzag" switching between segments and skipping points leading to a resolution which is approx GRAPH_CONNECTION_DISTANCE and not PRECISION * REDUCTION_DISTANCE.
  * Resolved by introducing costs to the graph and using Dijkstra
* ID2:
  * Annotate points with original route
