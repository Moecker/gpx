# GPX Bike Path Creator
##
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
python3 facade.py  --start Basel --end Zurich --gpx bikeline\\ch
```

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
* Create requirements.txt with `python3 -m  pipreqs.pipreqs . --force`
