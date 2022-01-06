import argparse
import os

import flask
from flask import jsonify, request

import facade

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route("/", methods=["GET"])
def home():
    return """<h1>Usage</h1><p>Start City: 'start'</p><p>End City: 'end'</p><p>Example: /api/path?start=Dachau&end=Augsburg</p>"""


@app.route("/api/path", methods=["GET"])
def api_id():
    if not "start" in request.args:
        return "No 'start' field provided."
    if not "end" in request.args:
        return "No 'end' field provided."

    start = request.args["start"]
    end = request.args["end"]

    return run(start, end)


def run(start, end):
    args = argparse.Namespace(
        start=start,
        end=end,
        gpx=os.path.join("adfc"),
        interactive=False,
        verbose=True,
        dry=False,
    )

    path = facade.main(args)

    if not path:
        return "Error during path finding."

    with open("results/1_dijkstra_rescaled.html") as f:
        return f.read()


if __name__ == "__main__":
    app.run()
