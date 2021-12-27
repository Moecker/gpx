import logging
import os

import gpxpy


class SimplePoint:
    def __init__(self, point):
        self.latitude = point[0]
        self.longitude = point[1]

    @classmethod
    def from_gpx_point(cls, gpx_point):
        return cls((gpx_point.latitude, gpx_point.longitude))

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"GPS:{hex(id(self))}:({self.latitude:.8f},{self.longitude:.8f})"


class SimpleSegment:
    def __init__(self, segment):
        self.points = []
        for point in segment.points:
            self.points.append(SimplePoint.from_gpx_point(point))


def simplify_segment(segment):
    new_segment = SimpleSegment(segment)
    return new_segment


def save_as_gpx_file(points, dir, file_name):
    gpx = gpxpy.gpx.GPX()

    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    file_path = os.path.join(dir, file_name)
    if points:
        logging.info(f"Saving {len(points)} points to {file_path}.")
    else:
        logging.error(f"Cannot save {file_name}, no points found.")
        return

    for point in points:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(point.latitude, point.longitude))

    with open(file_path, "w") as f:
        f.write(gpx.to_xml())
