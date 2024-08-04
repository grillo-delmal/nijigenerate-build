#!/bin/bash

LD_LIBRARY_PATH=$(pwd)/build_out/nijiexpose:${LD_LIBRARY_PATH} \
    ./build_out/nijiexpose/nijiexpose $1
