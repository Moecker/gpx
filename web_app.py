import argparse
import logging
import os
from pathlib import Path

import flask
from flask import request

import config
import facade

app = flask.Flask(__name__)
app.config["DEBUG"] = True


class Globals:
    cities = None
    segments_dict = None
    background = None
    map = None


def get_form(start, end, paths):
    return f"""
    <form action="/path">
        <input name="start" value="{start}">
        <input name="end" value="{end}">
        <input name="paths" value="{paths}">
        <button>Search</button>
    </form>
    """.strip()


@app.route("/", methods=["GET"])
def home():
    return build_html(os.path.join("data", "map_template.html"), "Dachau", "Frankfurt", "1")


@app.route("/path", methods=["GET"])
def api_id():
    start = request.args["start"]
    end = request.args["end"]
    paths = request.args["paths"]

    return run(start, end, paths)


def load():
    logging.debug("Setting up web app globals.")
    args = argparse.Namespace(gpx=config.WEB_APP_SOURCE, interactive=False, verbose=True, dry=True, web_app=True)
    facade_ret = facade.main(args)

    if len(facade_ret) != 4:
        logging.error("Error during preloading phase.")
        exit()

    Globals.cities, Globals.segments_dict, Globals.background, Globals.map = facade_ret

    if not Globals.cities or not Globals.segments_dict or not Globals.background or not Globals.map:
        logging.error("Error during loading phase.")
        exit()


def read_and_show_log():
    with open(os.path.join("tmp", "web_app_log.txt")) as f:
        lines = f.readlines()

    filtered = []
    for line in reversed(lines):
        if ":" in line:
            filtered.append(line)
    return "<br>".join(filtered)


def build_html(map_html, start, end, paths):
    with open(map_html) as f:
        content = f.readlines()
        result = []
        for c in content:
            result.append(c)
            if c.startswith("<body>"):
                result.append(get_form(start, end, paths))
        return "\n".join(result)


def run(start, end, paths):
    logging.info("New web app run.")
    config.NUMBER_OF_PATHS = int(paths)
    dijkstra_rescaled, old_weights_data = facade.normal_mode(
        Globals.cities, start, end, Globals.segments_dict, Globals.background, Globals.map, True
    )
    facade.readjust_weights(old_weights_data, Globals.map)

    if not dijkstra_rescaled:
        return read_and_show_log()

    return build_html("results/path.html", start, end, paths)


if __name__ == "__main__":
    Path("tmp").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s:%(msecs)03d %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.FileHandler(os.path.join("tmp", "web_app_log.txt"), mode="w"), logging.StreamHandler()],
    )
    load()
    app.run(host="0.0.0.0", port=8090, use_reloader=False)
