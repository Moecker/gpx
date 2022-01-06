# Thing to do

* ID1:
  * (DONE) Given that segments can be very similar, we often see points "skipped" because segment1 can connect to segment2 by GRAPH_CONNECTION_DISTANCE which, in case segment1 and segment2 are very similar, can lead to "zigzag" switching between segments and skipping points leading to a resolution which is approx GRAPH_CONNECTION_DISTANCE and not PRECISION * REDUCTION_DISTANCE.
  * Resolved by introducing costs to the graph and using Dijkstra
* ID2:
  * (DONE) Annotate points with original path
* ID3:
  * (DONE) How come that it says "Rescaled from 43 to 0 points"? -> Directions did matter, but should not.
* ID4:
  * (DONE) Select multiple possible path: https://softwareengineering.stackexchange.com/questions/232305/a-with-possible-multiple-paths
* ID5:
  * (DONE) Use python C++ binding to speed up
* ID6:
  * (DONE) Only use those nodes which are possible segment change (or shortcuts) into the map
