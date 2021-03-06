from pprint import pformat
import logging

import distance
import utils


def walk_gpx(walk_segment_name, segments_dict, min_end_distance, end_gps, route, routes, current_distance):
    ROUTES_FOUND_END = 1  # Max number of requested routes
    MAX_DETOUR = 5.0  # in km
    MAX_END_DISTANCE = 10.0  # in km
    MIN_GAP_DIS = 5.0  # in km
    POINTS_ITERATOR_GAP = 10.0  # in km

    print("Walk")
    if len(routes) >= ROUTES_FOUND_END:
        return

    if walk_segment_name in segments_dict.keys():
        walk_segment = segments_dict[walk_segment_name]
        route.append(walk_segment_name)
    else:
        logging.debug(f"Skipping {utils.simple_name(walk_segment_name)}, has been seen before.")
        return

    segments_dict.pop(walk_segment_name)

    logging.debug(f"Walking {len(walk_segment.points)} points on {walk_segment_name}.")

    for walk_point in walk_segment.points[::POINTS_ITERATOR_GAP]:
        for name, segment in segments_dict.copy().items():
            if name != walk_segment_name:
                for idx, point in enumerate(segment.points[::POINTS_ITERATOR_GAP]):
                    dist = distance.haversine_gpx(walk_point, point)

                    if dist < MIN_GAP_DIS:
                        logging.debug(
                            f"Switch from {utils.simple_name(walk_segment_name)} to {utils.simple_name(name)} at point id {idx} possible distanced by {dist} km."
                        )
                        walk_gpx(name, segments_dict, min_end_distance, end_gps, route, routes, current_distance)
                        break

        to_end_dist = distance.haversine_gpx(walk_point, end_gps)
        if to_end_dist < (min_end_distance + MAX_END_DISTANCE):
            tupled = tuple(route)
            if not tupled in routes:
                routes.add(tuple(route))
                logging.info(f"New route found following {pformat(route)}.")

        if to_end_dist < current_distance:
            current_distance = to_end_dist

        if to_end_dist > (current_distance + MAX_DETOUR):
            logging.debug(f"Detour of {to_end_dist} km to end, skipping.")
            return
