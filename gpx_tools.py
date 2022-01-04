import logging
import os
import config
import gpxpy
import utils
import gpx_tools

import cpp.point.point as point_cpp


class SimplePoint:
    def __init__(self, point):
        self.latitude = point[0]
        self.longitude = point[1]
        self.annotation = ""
        self.source = ""

    @classmethod
    def from_gpx_point(cls, gpx_point):
        point = cls((gpx_point.latitude, gpx_point.longitude))
        point.source = gpx_point.source
        return point

    def short(self):
        pre = f"[{self.source}]" if self.source else ""
        return f"{pre}GPS({self.latitude:.4f},{self.longitude:.4f})"

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        post = f"[{utils.make_path_clickable(self.annotation)}]" if self.annotation else ""
        pre = f"[{self.source}]" if self.source else ""
        return f"{pre}GPS({self.latitude:.4f},{self.longitude:.4f}){post}"

    def __lt__(self, other):
        return True

    def __le__(self, other):
        return True


class SimpleSegment:
    def __init__(self, segment):
        self.points = []
        for point in segment.points:
            p = (
                point_cpp.Point(point.latitude, point.longitude)
                if config.USE_CPP
                else SimplePoint.from_gpx_point(point)
            )
            self.points.append(p)


def annotate(point, name, idx):
    point.annotation = f"{name}@{idx}"


def deannotate(point):
    annotations = point.annotation.split("@")
    key = annotations[0]
    idx = int(annotations[1])
    return key, idx


def save_as_gpx_file(points, dir, file_name, max_points):
    gpx = gpxpy.gpx.GPX()

    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    file_path = os.path.join(dir, file_name)
    if points:
        logging.info(f"Saving GPX path of {len(points)} points to '{utils.make_path_clickable(file_path)}'.")
    else:
        logging.error(f"Cannot save '{utils.make_path_clickable(file_name)}', no points found.")
        return

    step_size = int(max(1, len(points) / max_points))
    if step_size > 1:
        logging.warning(f"Too many points, reducing to every {step_size}th point.")
    for point in points[::step_size]:
        key, idx = gpx_tools.deannotate(point)
        track_point = gpxpy.gpx.GPXTrackPoint(point.latitude, point.longitude)
        track_point.source = f"{key}@{idx}"
        gpx_segment.points.append(track_point)

    with open(file_path, "w") as f:
        f.write(gpx.to_xml())


def simplify_segment(segment):
    new_segment = SimpleSegment(segment)
    return new_segment
