import logging
import os

import gpxpy

import utils

COLORS = ["blue", "red"]


def overlay_gpx(gpx_data_files, zoom):
    # Import only when using, improves runtime.
    import folium

    """
    Overlay a gpx route on top of an OSM map using Folium
    some portions of this function were adapted
    from this post: https://stackoverflow.com/questions/54455657/
    how-can-i-plot-a-map-using-latitude-and-longitude-data-in-python-highlight-few
    """
    for idx, gpx_data_file in enumerate(gpx_data_files):
        with open(gpx_data_file, "r") as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append(tuple([point.latitude, point.longitude]))

        latitude = sum(p[0] for p in points) / len(points)
        longitude = sum(p[1] for p in points) / len(points)

        map = folium.Map(location=[latitude, longitude], zoom_start=zoom)
        folium.PolyLine(points, color=COLORS[idx], weight=2.5, opacity=1).add_to(map)

    return map


def save_gpx_as_html(map_names, dir):
    gpx_file_paths = []

    if len(map_names) > 1:
        html_file_path = os.path.join(dir, f"paths.html")
    else:
        # Backwards compatibility for a single path
        html_file_path = os.path.join(dir, f"{map_names[0]}.html")

    for map_name in map_names:
        gpx_file_path = os.path.join(dir, f"{map_name}.gpx")
        gpx_file_paths.append(gpx_file_path)

        logging.info(
            f"Saving '{utils.make_path_clickable(gpx_file_path)}' as HTML Map to '{utils.make_path_clickable(html_file_path)}'."
        )

        if not os.path.isfile(gpx_file_path):
            logging.error(
                f"Cannot convert '{utils.make_path_clickable(gpx_file_path)}' to HTML, input file does not exist."
            )
            return

    map = overlay_gpx(gpx_file_paths, zoom=8)
    map.save(f"{html_file_path}")
