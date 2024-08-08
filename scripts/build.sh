#!/usr/bin/bash

set -e

source /opt/scripts/semver.sh
source /opt/scripts/cimgui.sh

# Clean out folder
find /opt/out/ -mindepth 1 -maxdepth 1 -exec rm -r -- {} +

echo "======== Loading sources ========"

cd /opt
mkdir -p src

rsync --info=progress2 -azh /opt/orig/nijigenerate/ /opt/src/nijigenerate/
rsync --info=progress2 -azh /opt/orig/nijiexpose/ /opt/src/nijiexpose/

rsync --info=progress2 -azh /opt/orig/nijilive/ /opt/src/nijilive/
rsync --info=progress2 -azh /opt/orig/nijiui/ /opt/src/nijiui/

echo "======== Applying patches ========"

if [ -d ./patches ]; then
    pushd patches
    if [ ! -z "$(ls -A */ 2> /dev/null)" ]; then
        for d in */ ; do
            for p in ${d}*.patch; do
                echo "patch /opt/patches/$p"
                git -C /opt/src/${d} apply /opt/patches/$p
            done
        done
    fi
    popd
fi

cat > /opt/src/nijigenerate/source/nijigenerate/ver.d <<EOF
module nijigenerate.ver;

enum INC_VERSION = "$(semver /opt/src/nijigenerate/)";
EOF

cat > /opt/src/nijiexpose/source/nijiexpose/ver.d <<EOF
module nijiexpose.ver;

enum INS_VERSION = "$(semver /opt/src/nijiexpose/)";
EOF

cat > /opt/src/nijilive/source/nijilive/ver.d <<EOF
module nijilive.ver;

enum IN_VERSION = "$(semver /opt/src/nijilive/)";
EOF

if [[ ! -z ${LOAD_CACHE} ]]; then

    echo "======== Loading cache ========"

    mkdir -p /opt/cache/.dub/
    rsync --info=progress2 -azh /opt/cache/.dub/ ~/.dub/

    rm -f /opt/cache/.dub/packages/local-packages.json
fi

echo "======== Loading dub dependencies ========"

# Add dlang deps
dub add-local /opt/src/nijilive/        "$(semver /opt/src/nijilive/ 0.0.1)"
dub add-local /opt/src/nijiui/          "$(semver /opt/src/nijiui/ 0.0.1)"

if [[ ! -z ${NIJIGENERATE} ]]; then
    echo "======== Starting nijigenerate ========"

    # Build nijigenerate
    pushd src
    pushd nijigenerate

    # Gen tl files
    chmod +x ./gentl.sh
    ./gentl.sh

    if [[ ! -z ${DEBUG} ]]; then
        export DFLAGS='-g --d-debug'
    fi
    export DC='/usr/bin/ldc2'
    if [[ ! -z ${PREDOWNLOAD_LIBS} ]]; then
        echo "======== Downloading nijigenerate libs ========"
        echo "Download time" > /opt/out/nijigenerate-stats 
        if [[ -z ${LOAD_CACHE} ]]; then

            { time \
                dub describe \
                    --config=linux-full \
                    --cache=user \
                        2>&1 > /opt/out/nijigenerate-describe ; \
                }  2>> /opt/out/nijigenerate-stats 
        else
            { time \
                dub describe \
                    --config=linux-full \
                    --cache=user \
                    --skip-registry=all \
                        2>&1 > /opt/out/nijigenerate-describe ; \
                }  2>> /opt/out/nijigenerate-stats 
        fi
        echo "" >> /opt/out/nijigenerate-stats 
    fi

    prepare_i2d_imgui

    echo "======== Building nijigenerate ========"
    echo "Build time" >> /opt/out/nijigenerate-stats 
    if [[ -z ${LOAD_CACHE} ]]; then
    { time \
        dub build \
            --config=linux-full \
            --cache=user \
                2>&1 ; \
        } 2>> /opt/out/nijigenerate-stats 
    else
        { time \
            dub build \
                --config=linux-full \
                --cache=user \
                --skip-registry=all \
                    2>&1 ; \
            } 2>> /opt/out/nijigenerate-stats 
    fi
    popd
    popd
fi

if [[ ! -z ${NIJIEXPOSE} ]]; then
    echo "======== Starting nijiexpose ========"

    # Build nijiexpose
    pushd src
    pushd nijiexpose
    mkdir -p out
    if [[ ! -z ${DEBUG} ]]; then
        export DFLAGS='-g --d-debug'
    fi
    export DC='/usr/bin/ldc2'
    if [[ ! -z ${PREDOWNLOAD_LIBS} ]]; then
        echo "======== Downloading nijiexpose libs ========"
        echo "Download time" > /opt/out/nijiexpose-stats 
        if [[ -z ${LOAD_CACHE} ]]; then
            { time \
                dub describe \
                    --config=linux-full \
                    --cache=user \
                    --override-config=facetrack-d/web-adaptors \
                        2>&1 > /opt/out/nijiexpose-describe ; \
                }  2>> /opt/out/nijiexpose-stats
        else
            { time \
                dub describe \
                    --config=linux-full \
                    --cache=user \
                    --override-config=facetrack-d/web-adaptors \
                    --skip-registry=all \
                        2>&1 > /opt/out/nijiexpose-describe ; \
                }  2>> /opt/out/nijiexpose-stats
        fi
        echo "" >> /opt/out/nijiexpose-stats 
    fi

    prepare_i2d_imgui

    echo "======== Building nijiexpose ========"
    echo "Build time" >> /opt/out/nijiexpose-stats 
    if [[ -z ${LOAD_CACHE} ]]; then
        { time \
            dub build \
                --config=linux-full \
                --cache=user \
                --override-config=facetrack-d/web-adaptors \
                    2>&1 ; \
            } 2>> /opt/out/nijiexpose-stats
    else
        { time \
            dub build \
                --config=linux-full \
                --cache=user \
                --override-config=facetrack-d/web-adaptors \
                --skip-registry=all \
                    2>&1 ; \
            } 2>> /opt/out/nijiexpose-stats
    fi
    popd
    popd
fi

echo "======== Getting results ========"

if [[ ! -z ${NIJIGENERATE} ]]; then
    # Install nijigenerate
    rsync -azh /opt/src/nijigenerate/out/ /opt/out/nijigenerate/
    echo "" >> /opt/out/nijigenerate-stats 
    echo "Result files" >> /opt/out/nijigenerate-stats 
    echo "" >> /opt/out/nijigenerate-stats 
    du -sh /opt/out/nijigenerate/* >> /opt/out/nijigenerate-stats 
fi

if [[ ! -z ${NIJIEXPOSE} ]]; then
    # Install nijiexpose
    rsync -azh /opt/src/nijiexpose/out/ /opt/out/nijiexpose/
    echo "" >> /opt/out/nijiexpose-stats 
    echo "Result files" >> /opt/out/nijiexpose-stats 
    echo "" >> /opt/out/nijiexpose-stats 
    du -sh /opt/out/nijiexpose/* >> /opt/out/nijiexpose-stats
fi

# ---
dub list > /opt/out/version_dump

if [[ ! -z ${SAVE_CACHE} ]]; then
    echo "======== Saving cache ========"

    if [[ -z ${LOAD_CACHE} ]]; then
        find /opt/cache/ -mindepth 1 -maxdepth 1 -exec rm -r -- {} +
    fi

    mkdir -p /opt/cache/.dub/
    rsync --info=progress2 -azh ~/.dub/ /opt/cache/.dub/

fi

