#!/bin/bash

set -euo pipefail

find . -iname *.h -o -iname *.cpp | xargs clang-format -i

pushd graph
pip3 install -e .
popd

pushd point
pip3 install -e .
popd

python3 main.py
