#!/bin/bash

set -euo pipefail

if command -v clang-format &> /dev/null; then
    find . -iname *.h -o -iname *.cpp | xargs clang-format -i
fi

if command -v black &> /dev/null; then
    black .  --line-length 120
fi

pushd cpp/graph
python3 -m pip install --user -e .
popd

pushd cpp/point
python3 -m pip install --user -e .
popd

python3 test_cpp.py
