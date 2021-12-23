import gpxpy
import distance as distance

munich = (48.13743, 11.57549)
gps = gpxpy.gpx.GPXTrackPoint(munich[0], munich[1])

print(distance.haversine(munich, (gps.latitude, gps.longitude)))

gpx_file = open("data/example.gpx", "r")

gpx = gpxpy.parse(gpx_file)

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            print(point)
