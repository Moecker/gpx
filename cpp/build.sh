#!/bin/bash

clang-format **/*.h **/*.cpp  -i

pushd graph
pip3 install -e .
popd
