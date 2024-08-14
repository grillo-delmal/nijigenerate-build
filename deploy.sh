#!/usr/bin/bash

set -e

DEBUG=
PREBUILD_IMGUI=1
PREDOWNLOAD_LIBS=1
NIJIGENERATE=1
NIJIEXPOSE=1
LOAD_CACHE=
SAVE_CACHE=1

podman build -t nijilive-build .

mkdir -p $(pwd)/build_out
mkdir -p $(pwd)/cache

podman unshare chown $UID:$UID -R $(pwd)/build_out
podman unshare chown $UID:$UID -R $(pwd)/cache

podman run -ti --rm \
    -v $(pwd)/build_out:/opt/out/:Z \
    -v $(pwd)/cache:/opt/cache/:Z \
    -v $(pwd)/.git:/opt/.git/:ro,Z \
    -v $(pwd)/src/nijigenerate:/opt/orig/nijigenerate/:ro,Z \
    -v $(pwd)/src/nijiexpose:/opt/orig/nijiexpose/:ro,Z \
    -v $(pwd)/src/nijilive:/opt/orig-deps/nijilive/:ro,Z \
    -v $(pwd)/src/nijiui:/opt/orig-deps/nijiui/:ro,Z \
    -v $(pwd)/patches:/opt/patches/:ro,Z \
    -v $(pwd)/files:/opt/files/:ro,Z \
    -v $(pwd)/scripts:/opt/scripts/:ro,Z \
    -w /opt/scripts/ \
    -e PREBUILD_IMGUI=${PREBUILD_IMGUI} \
    -e PREDOWNLOAD_LIBS=${PREDOWNLOAD_LIBS} \
    -e NIJIGENERATE=${NIJIGENERATE} \
    -e NIJIEXPOSE=${NIJIEXPOSE} \
    -e DEBUG=${DEBUG} \
    -e LOAD_CACHE=${LOAD_CACHE} \
    -e SAVE_CACHE=${SAVE_CACHE} \
    localhost/nijilive-build:latest \
    bash build.sh

podman unshare chown 0:0 -R $(pwd)/build_out
podman unshare chown 0:0 -R $(pwd)/cache
