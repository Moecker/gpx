import folium
import gpxpy
import os


def overlay_gpx(gpxData, zoom):
    """
    overlay a gpx route on top of an OSM map using Folium
    some portions of this function were adapted
    from this post: https://stackoverflow.com/questions/54455657/
    how-can-i-plot-a-map-using-latitude-and-longitude-data-in-python-highlight-few
    """
    gpx_file = open(gpxData, "r")
    gpx = gpxpy.parse(gpx_file)
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append(tuple([point.latitude, point.longitude]))
    latitude = sum(p[0] for p in points) / len(points)
    longitude = sum(p[1] for p in points) / len(points)
    map = folium.Map(location=[latitude, longitude], zoom_start=zoom)
    folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(map)
    return map


file_name = "example.gpx"
file_path = os.path.join("data", file_name)

map = overlay_gpx(file_path, 14)
map.save(os.path.join("output", "map.html"))