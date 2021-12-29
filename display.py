import os


import folium
import gpxpy
import logging


def overlay_gpx(gpx_data_file, zoom):
    """
    overlay a gpx route on top of an OSM map using Folium
    some portions of this function were adapted
    from this post: https://stackoverflow.com/questions/54455657/
    how-can-i-plot-a-map-using-latitude-and-longitude-data-in-python-highlight-few
    """
    gpx_file = open(gpx_data_file, "r")
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


def save_gpx_as_html(map_name, dir):
    gpx_file_path = os.path.join(dir, f"{map_name}.gpx")
    html_file_path = os.path.join(dir, f"{map_name}.html")

    if not os.path.isfile(gpx_file_path):
        logging.error(f"Cannot save {gpx_file_path} to {html_file_path}, input file does not exist.")
        return

    logging.info(f"Saving '{gpx_file_path}' as HTML Map to '{html_file_path}'.")

    map = overlay_gpx(gpx_file_path, zoom=8)
    map.save(f"{html_file_path}")
