import gpxpy
import logging
import os

class SimplePoint:
    def __init__(self, point):
        self.latitude = point[0]
        self.longitude = point[1]

    @classmethod
    def from_gpx_point(cls, gpx_point):
        return cls((gpx_point.latitude, gpx_point.longitude))

    def __str__(self):
        return f"({self.latitude:.2f}, {self.longitude:.2f})"


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

    file_path =  os.path.join(dir, file_name)
    logging.info(f"Saving {len(points)} points to {file_path}.")
    for point in points:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(point.latitude, point.longitude))

    with open(file_path, "w") as f:
        f.write(gpx.to_xml())