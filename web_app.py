import argparse
import os

import flask
from flask import request
import logging
import facade

app = flask.Flask(__name__)
app.config["DEBUG"] = True


class Globals:
    cities = None
    segments_dict = None
    background = None
    map = None


@app.route("/", methods=["GET"])
def home():
    with open("form.html") as f:
        return f.read()


@app.route("/api/path", methods=["GET"])
def api_id():
    if not "start" in request.args:
        return "No 'start' field provided."
    if not "end" in request.args:
        return "No 'end' field provided."

    start = request.args["start"]
    end = request.args["end"]

    return run(start, end)


def load():
    args = argparse.Namespace(gpx=os.path.join("adfc"), interactive=False, verbose=True, dry=False, web_app=True)
    Globals.cities, Globals.segments_dict, Globals.background, Globals.map = facade.main(args)


def read_and_show_log():
    with open(os.path.join("tmp", "web_app_log.txt")) as f:
        lines = f.readlines()

    filtered = []
    for line in reversed(lines):
        if ":" in line:
            filtered.append(line)
    return "<br>".join(filtered)


def run(start, end):
    logging.info("")
    dijkstra, dijkstra_rescaled = facade.perform_run(
        Globals.cities, start, end, Globals.segments_dict, Globals.background, Globals.map, False, 0
    )

    if not dijkstra or not dijkstra_rescaled:
        return read_and_show_log()

    with open("results/0_dijkstra_rescaled.html") as f:
        return f.read()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s:%(msecs)03d %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.FileHandler(os.path.join("tmp", "web_app_log.txt"), mode="w"), logging.StreamHandler()],
    )
    load()
    app.run(port=8080)
