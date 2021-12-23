import gpxpy
import distance as distance

munich = (48.13743, 11.57549)
gps = gpxpy.gpx.GPXTrackPoint(munich[0], munich[1])

print(gps)

dachau = (48.2629984, 11.4339022)

london_coord = 51.5073219,  -0.1276474
cities = {
    'berlin': (52.5170365,  13.3888599),
    'munich': (48.13743, 11.57549),
    'vienna': (48.2083537,  16.3725042),
    'sydney': (-33.8548157, 151.2164539),
    'madrid': (40.4167047,  -3.7035825)
}

for city, coord in cities.items():
    diff = distance.haversine(dachau, coord)
    print(city, diff)
