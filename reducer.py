import gpxpy


def reduce(file_name, min_dis, file_name_reduced):
    with open(file_name, "r") as f:
        track = gpxpy.parse(f)
        track.reduce_points(min_distance=min_dis)

    with open(file_name_reduced, "w") as f:
        f.write(track.to_xml())
