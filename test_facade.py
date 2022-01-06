import argparse
import logging
import os
import unittest
import networkx as nx

import config
import facade


def reset_config():
    # Resets those configs which are always required as the testing framework would else not work.
    # Also reset config options which are non default in order to be able to test more easily.
    # Every single test will use those before being executed, avoiding to use the changed
    # configs from other test runs.
    config.ALWAYS_GRAPH = True
    config.ALWAYS_PARSE = True
    config.ALWAYS_REDUCE = True
    config.COST_NORMAL_PENALTY = 1
    config.COST_SWITCH_SEGMENT_PENALTY = 1
    config.COST_ALREADY_VISITED_PENALTY = 100
    config.GRAPH_CONNECTION_DISTANCE = 1
    config.HEURISTIC_SCALE_FACTOR = 10
    config.IS_TEST = True
    config.MAX_POINTS = 10000
    config.MAX_POINTS_OVERVIEW = 1000
    config.NUMBER_OF_PATHS = 1
    config.PRECISION = 1
    config.REDUCTION_DISTANCE = 1
    config.RESULTS_FOLDER = os.path.join("test", "results")
    config.SCALE_FACTOR = 50
    config.STORAGE_TEMP_DIR = os.path.join("test", "tmp")
    config.USE_CPP = False
    config.USE_NETWORK_X = True
    config.USE_PICKLE = True
    config.USE_SMART = True
    config.USE_INEXACT_STEP_DISTANCE = False


AUGSBURG = (48.3717, 10.8983)
DACHAU = (48.2603, 11.4342)
FREISING = (48.4028, 11.7489)
FURSTENFELDBRUCK = (48.1778, 11.2556)
MUNICH = (48.1372, 11.5755)


class TestFacade(unittest.TestCase):
    def setUp(self):
        reset_config()
        config.USE_NETWORK_X = False

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
        self.compare_points(dijkstra_rescaled[2], DACHAU)

    def test_munich_dachau_multiple_segments(self):
        args = argparse.Namespace(
            start="Munich",
            end="Dachau",
            gpx=os.path.join("test", "gpx", "test_munich_dachau_detour"),
            interactive=False,
            verbose=True,
            dry=False,
        )
        dijkstra_rescaled = facade.main(args)
        self.assertEqual(len(dijkstra_rescaled), 2)
        self.compare_points(dijkstra_rescaled[0], MUNICH)
        self.compare_points(dijkstra_rescaled[1], DACHAU)

    def test_munich_dachau_detour_no_path(self):
        args = argparse.Namespace(
            start="Munich",
            end="Freising",
            gpx=os.path.join("test", "gpx", "test_munich_dachau_detour"),
            interactive=False,
            verbose=True,
            dry=False,
        )
        if config.USE_NETWORK_X:
            self.assertRaises(nx.exception.NetworkXNoPath, facade.main, args)
        else:
            dijkstra_rescaled = facade.main(args)
            self.assertEqual(dijkstra_rescaled, [])

    def test_munich_dachau_detour_big_segment_distance(self):
        config.GRAPH_CONNECTION_DISTANCE = 100
        args = argparse.Namespace(
            start="Munich",
            end="Freising",
            gpx=os.path.join("test", "gpx", "test_munich_dachau_detour"),
            interactive=False,
            verbose=True,
            dry=False,
        )
        dijkstra_rescaled = facade.main(args)
        self.assertEqual(len(dijkstra_rescaled), 2)
        self.compare_points(dijkstra_rescaled[0], MUNICH)
        self.compare_points(dijkstra_rescaled[1], FREISING)

    def test_munich_dachau_detour_high_switch_cost(self):
        config.GRAPH_CONNECTION_DISTANCE = 100
        config.COST_SWITCH_SEGMENT_PENALTY = 100
        args = argparse.Namespace(
            start="Munich",
            end="Freising",
            gpx=os.path.join("test", "gpx", "test_munich_dachau_detour"),
            interactive=False,
            verbose=True,
            dry=False,
        )
        dijkstra_rescaled = facade.main(args)
        self.assertEqual(len(dijkstra_rescaled), 3)
        self.compare_points(dijkstra_rescaled[0], MUNICH)
        self.compare_points(dijkstra_rescaled[1], DACHAU)
        self.compare_points(dijkstra_rescaled[2], FREISING)

    def test_munich_augsburg_intersection(self):
        config.COST_SWITCH_SEGMENT_PENALTY = 100
        args = argparse.Namespace(
            start="Munich",
            end="Augsburg",
            gpx=os.path.join("test", "gpx", "test_munich_augsburg_intersection"),
            interactive=False,
            verbose=True,
            dry=False,
        )
        dijkstra_rescaled = facade.main(args)
        self.assertEqual(len(dijkstra_rescaled), 4)
        self.compare_points(dijkstra_rescaled[0], MUNICH)
        self.compare_points(dijkstra_rescaled[1], FURSTENFELDBRUCK)
        self.compare_points(dijkstra_rescaled[2], FURSTENFELDBRUCK)
        self.compare_points(dijkstra_rescaled[3], AUGSBURG)

    def test_long(self):
        args = argparse.Namespace(
            start="Munich",
            end="Augsburg",
            gpx=os.path.join("test", "gpx", "long"),
            interactive=False,
            verbose=True,
            dry=False,
        )
        dijkstra_rescaled = facade.main(args)
        self.assertEqual(len(dijkstra_rescaled), 4)
        self.compare_points(dijkstra_rescaled[0], MUNICH)
        self.compare_points(dijkstra_rescaled[1], FURSTENFELDBRUCK)
        self.compare_points(dijkstra_rescaled[2], FURSTENFELDBRUCK)
        self.compare_points(dijkstra_rescaled[3], AUGSBURG)

    def test_example(self):
        config.GRAPH_CONNECTION_DISTANCE = 10
        config.USE_SMART = False
        args = argparse.Namespace(
            start="Erfurt",
            end="Leipzig",
            gpx=os.path.join("test", "gpx", "example"),
            interactive=False,
            verbose=True,
            dry=False,
        )
        dijkstra_rescaled = facade.main(args)


class TestFacadeNetworkX(TestFacade):
    def setUp(self):
        reset_config()
        config.USE_NETWORK_X = True


def main():
    unittest.main()


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    unittest.main()
