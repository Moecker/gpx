import facade

import unittest
import argparse
import os
import config


def default_test_setup():
    # Those are always required as the testing framework would else not work.
    config.ALWAYS_GRAPH = True
    config.ALWAYS_PARSE = True
    config.ALWAYS_REDUCE = True
    config.STORAGE_TEMP_DIR = os.path.join("test", "tmp")
    config.RESULTS_FOLDER = os.path.join("test", "results")


def default_adjusted_params():
    # Config options which are non default in order to be able to test more easily.
    config.PRECISION = 1
    config.NUMBER_OF_PATHS = 1


MUNICH = (48.1372, 11.5755)
DACHAU = (48.2603, 11.4342)
FURSTENFELDBRUCK = (48.1778, 11.2556)
FREISING = (48.4028, 11.7489)


class TestFacade(unittest.TestCase):
    def setUp(self):
        default_test_setup()
        default_adjusted_params()

    def compare_points(self, gpx_point, coord):
        self.assertEqual(gpx_point.latitude, coord[0])
        self.assertEqual(gpx_point.longitude, coord[1])

    def test_munich_dachau(self):
        args = argparse.Namespace(
            start="Munich",
            end="Dachau",
            gpx=os.path.join("test", "gpx", "test_munich_dachau"),
            interactive=False,
            verbose=True,
            dry=False,
        )
        dijkstra_rescaled = facade.main(args)
        self.assertEqual(len(dijkstra_rescaled), 2)
        self.compare_points(dijkstra_rescaled[0], MUNICH)
        self.compare_points(dijkstra_rescaled[-1], DACHAU)

    def test_munich_furstenfeldbruck_dachau(self):
        args = argparse.Namespace(
            start="Munich",
            end="Dachau",
            gpx=os.path.join("test", "gpx", "test_munich_furstenfeldbruck_dachau"),
            interactive=False,
            verbose=True,
            dry=False,
        )
        dijkstra_rescaled = facade.main(args)
        self.assertEqual(len(dijkstra_rescaled), 3)
        self.compare_points(dijkstra_rescaled[0], MUNICH)
        self.compare_points(dijkstra_rescaled[1], FURSTENFELDBRUCK)
        self.compare_points(dijkstra_rescaled[-1], DACHAU)

    def test_munich_dachau_multiple_segments(self):
        args = argparse.Namespace(
            start="Munich",
            end="Dachau",
            gpx=os.path.join("test", "gpx", "test_munich_dachau_detour"),
            interactive=False,
            verbose=True,
            dry=True,
        )
        dijkstra_rescaled = facade.main(args)
        self.assertEqual(len(dijkstra_rescaled), 2)
        self.compare_points(dijkstra_rescaled[0], MUNICH)
        self.compare_points(dijkstra_rescaled[-1], DACHAU)

    def test_munich_dachau_detour_no_path(self):
        args = argparse.Namespace(
            start="Munich",
            end="Freising",
            gpx=os.path.join("test", "gpx", "test_munich_dachau_detour"),
            interactive=False,
            verbose=True,
            dry=True,
        )
        dijkstra_rescaled = facade.main(args)
        self.assertEqual(dijkstra_rescaled, None)

    def test_munich_dachau_detour_big_segment_distance(self):
        config.GRAPH_CONNECTION_DISTANCE = 100.0
        args = argparse.Namespace(
            start="Munich",
            end="Freising",
            gpx=os.path.join("test", "gpx", "test_munich_dachau_detour"),
            interactive=False,
            verbose=True,
            dry=True,
        )
        dijkstra_rescaled = facade.main(args)
        self.assertEqual(len(dijkstra_rescaled), 2)
        self.compare_points(dijkstra_rescaled[0], MUNICH)
        self.compare_points(dijkstra_rescaled[-1], FREISING)


if __name__ == "__main__":
    unittest.main()
