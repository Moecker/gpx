#!/bin/bash

set -euo pipefail

find . -iname *.h -o -iname *.cpp | xargs clang-format -i
black .  --line-length 120

pushd cpp/graph
pip3 install -e .
popd

python3 cpp.py
