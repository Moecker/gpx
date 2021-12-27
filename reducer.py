import gpxpy
import logging

def reduce(file_name, min_dis, file_name_reduced):
    with open(file_name, "r") as f:
        try:
            track = gpxpy.parse(f)
            track.reduce_points(min_distance=min_dis)
        except:
            # To interfer with tqpm
            print(f"\nERROR: Error while parsing and reducing {file_name} to {file_name_reduced}.")
            return False

    with open(file_name_reduced, "w") as f:
        f.write(track.to_xml())

    return True
