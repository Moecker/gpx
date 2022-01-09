import display
import glob
import config
import os
import logging
import random


def visualize_gpx_files(pattern, name):
    file_names = glob.glob(pattern)
    logging.info(f"Found {len(file_names)} gpx files")

    colors = ["#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)]) for i in range(len(file_names))]

    file_names = [f.replace(".gpx", "") for f in file_names]

    display.save_gpx_as_html(file_names, "", os.path.join("results", name), colors)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    visualize_gpx_files("tmp/1000/1000_bikeline_de*", "bikeline_de.html")
