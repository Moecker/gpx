import gpxpy
import gpxpy.gpx
import distance as distance
import math
import os

munich = (48.13743, 11.57549)
munich_gps = gpxpy.gpx.GPXTrackPoint(munich[0], munich[1])

min_dis = 1000.0
gpx_file_name = "bikeline/de/trk00dk472.gpx"
gpx_file_name = "bikeline/de/trk00fp446.gpx"
reduced_file_name = os.path.join("output", str(int(min_dis)) + "_" + gpx_file_name.replace("/", "_"))
gpx_file = open(reduced_file_name, "r")

gpx = gpxpy.parse(gpx_file)

points = 0
min_distance = math.inf

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            dis = distance.haversine_gpx(point, munich_gps)
            if dis < min_distance:
                min_distance = dis
            points += 1
            print(f"{dis:.2f} km")
print(f"Minimum Distance: {min_distance:.2f} km")
print(f"{points} points")
