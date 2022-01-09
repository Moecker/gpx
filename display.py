import logging
import os

import gpxpy
import config
import utils

COLORS = ["blue", "red", "green", "yellow", "brown"]


def overlay_gpx(gpx_data_files, zoom, name=None):
    # Import only when using, improves runtime.
    import folium

    """
    Overlay a gpx route on top of an OSM map using Folium
    some portions of this function were adapted
    from this post: https://stackoverflow.com/questions/54455657/
    how-can-i-plot-a-map-using-latitude-and-longitude-data-in-python-highlight-few
    """
    polylines = []
    all_points = []

    # Append as many "black" paths as needed
    for i in range(len(COLORS), config.NUMBER_OF_PATHS + 1):
        COLORS.append("grey")

    for idx, gpx_data_file in enumerate(reversed(gpx_data_files)):
        with open(gpx_data_file, "r") as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append(tuple([point.latitude, point.longitude]))
        all_points.extend(points)

        polylines.append(folium.PolyLine(points, color=COLORS[len(gpx_data_files) - idx - 1], weight=2.5, opacity=1))

    latitude = sum(p[0] for p in all_points) / len(all_points)
    longitude = sum(p[1] for p in all_points) / len(all_points)

    map = folium.Map(location=[latitude, longitude], zoom_start=zoom)
    for polyline in polylines:
        polyline.add_to(map)

    return map


def save_gpx_as_html(map_names, dir, name):
    gpx_file_paths = []

    html_file_path = os.path.join(dir, f"{name}")

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

    map = overlay_gpx(gpx_file_paths, 8, html_file_path)
    map.save(f"{html_file_path}")
