# GPX Bike Path Creator
This project's goal is to plan a path from one city to another using only known bike paths.

Known bike paths are those which have an official label, like the "Isar Radweg", for instance.
A possible use case is to find routes for longer bike tours which only use those official paths.

# How it works
The database is created using GPX files. Those files are reduced as such that the distance between two points is constant in order to reduce the number of points. A Graph is being created and a A-Star algorithm employed to find the shortest path.

# Notes
The project is a playground project to dive into a set of topics:
* Python in general.
* Algorithms + data structures such as graphs and Dijkstra.
* Pybindings for C++.
* Small Web App using a python backend and an API.
* Optimizations to improve runtime.
* Exploring already available modules.

## Usage
```
usage: facade.py [-h] [--start START] [--end END] --gpx GPX [--verbose] [--interactive] [--dry] [--web_app]

GPX Path Planner.

optional arguments:
  -h, --help     show this help message and exit
  --start START  Start City.
  --end END      End City.
  --gpx GPX      Relative Path to GPX Data Source
  --verbose      Log out more details.
  --interactive  Interactively to allow for multiple queries.
  --dry          Do not create any output artifacts.
  --web_app      Use the facade to prepare the web app.
```

## Example
```
python3 facade.py  --start Basel --end Zurich --gpx bikelin/ch
```

## Web App
With `python3 web_app.py` a local server is spawned which acts as a user interface to the path finder.
![Path Example](img/web.png)

## Tests
```
python3 test_facade.py
```

## Runnables
* `facade.py`: The main entry point to find paths. Does everything, reducing GPS points, parsing and building a graph, and searching paths between start and end points.
* `web_app.py`: A web app using he facade API.

## Tests
All files starting with `test_` are considered tests.

## Map
During the implementation a small visualization of GPS positions has been developed.
```
              . .
              . . . .
              . .   .               .
                .     . . .     . . . .
                .       . . . . .     . .
              . . .         .           . . .
            . .                             .
      . . . .                               .
      . .                                   .
      .                                     .
      .                                     . .
    . .                                       .
  . .                                         . .
. .                                             .
.                                               .
. .                                             .
.                                               . .
.                                               .
.                                               . .
. .                                     . . . . .
. .                                 . . .
. .                               . .
  .                                 .
  .                                 . . .
  .                                     . .
  . . . . .                               .
          . .                             . .         .
            .                               . .     . . . . .
            .                               . . . . .       . . .
          . .                             . . .         x x x x .
          .                             . . . x x x x x x     x x x
          .                             . x x x               . . x x x
          .   . . . .                   x x                   .       x x x x x
        . . . . . . . . . . . . . x x x x .                   . .
      . .             . . . x x x x x                         .
  . . .               . . . x     . . .                       .
  .                     x x x . . . . . . .                 . .
. .                   . x . . .         . . . . .     . . . .
.   . .       . .   . x x .                     . . . .
. .   .     . . . . .     .
      . . . .     .


```

# Other
* Create requirements.txt with `python3 -m  pipreqs.pipreqs . --force`.
