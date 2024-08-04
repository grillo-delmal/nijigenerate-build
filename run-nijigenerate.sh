#!/bin/bash

LD_LIBRARY_PATH=$(pwd)/build_out/nijigenerate:${LD_LIBRARY_PATH} \
    ./build_out/nijigenerate/nijigenerate "$@"
