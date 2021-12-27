import gpxpy
import gpxpy.gpx

gpx_file = open("data/example.gpx", "r")

gpx = gpxpy.parse(gpx_file)

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            print("Point at ({0},{1}) -> {2}".format(point.latitude, point.longitude, point.elevation))

for waypoint in gpx.waypoints:
    print("waypoint {0} -> ({1},{2})".format(waypoint.name, waypoint.latitude, waypoint.longitude))

for route in gpx.routes:
    print("Route:")
    for point in route.points:
        print("Point at ({0},{1}) -> {2}".format(point.latitude, point.longitude, point.elevation))

print("GPX:", gpx.to_xml())
gpx = gpxpy.gpx.GPX()

gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)

gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1234, 5.1234, elevation=1234))
gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1235, 5.1235, elevation=1235))
gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1236, 5.1236, elevation=1236))

print("Created GPX:", gpx.to_xml())
