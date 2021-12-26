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
