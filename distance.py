import math


def haversine(coord1, coord2):
    """Distance in KM between two coordinates"""
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a)) / 1000


def fast_haversine(coord1, coord2):
    """Distance in KM between two coordinates"""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    x = lat2 - lat1
    y = (lon2 - lon1) * math.cos((lat2 + lat1) * 0.00872664626)
    return 111.319 * math.sqrt(x * x + y * y)


def haversine_gpx(gps1, gps2):
    """Distance in KM between two GPS points"""
    return fast_haversine((gps1.latitude, gps1.longitude), (gps2.latitude, gps2.longitude))
