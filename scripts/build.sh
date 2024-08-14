#!/usr/bin/bash

set -e

source /opt/scripts/semver.sh
source /opt/scripts/cimgui.sh

# Clean out folder
find /opt/out/ -mindepth 1 -maxdepth 1 -exec rm -r -- {} +

echo "======== Loading sources ========"

cd /opt
mkdir -p src
mkdir -p deps

rsync --info=progress2 -azh /opt/orig/nijigenerate/ /opt/src/nijigenerate/
rsync --info=progress2 -azh /opt/orig/nijiexpose/ /opt/src/nijiexpose/

if [ -d ./orig-deps ]; then
    pushd orig-deps
    if [ ! -z "$(ls -A */ 2> /dev/null)" ]; then
        for d in */ ; do
            if [ -d /opt/orig-deps/${d} ]; then
                rsync --info=progress2 -azh /opt/orig-deps/${d} /opt/deps/${d}
                ln -s /opt/deps/${d} /opt/src/${d::-1}

                pushd /opt/deps/${d}

                # Apply patches
                if [ -d /opt/patches/${d} ]; then
                    for p in /opt/patches/${d}*.patch; do
                        echo "patch $p /opt/deps/$d"
                        git apply $p
                    done
                fi

                if [ -f dub.sdl ]; then
                    dub convert -f json
                fi

                DEP_SEMVER=$(semver /opt/deps/${d})

                mv dub.json dub.json.base
                jq ". += {\"version\": \"${DEP_SEMVER}\"}" dub.json.base > dub.json.ver
                jq 'walk(if type == "object" then with_entries(select(.key | test("preBuildCommands*") | not)) else . end)' dub.json.ver > dub.json
                if [ $d == 'i2d-imgui/' ]; then
                    check_local_imgui
                fi
if [ $d == 'nijilive/' ]; then
cat > ./source/nijilive/ver.d <<EOF
module nijilive.ver;

enum IN_VERSION = "$(semver /opt/src/nijilive/)";
EOF
fi
                popd

                dub add-local /opt/deps/${d}
                rm /opt/src/${d::-1}
            fi
        done
    fi
    popd
fi

echo "======== Applying patches ========"

if [ -d ./patches ]; then
    pushd patches
    if [ ! -z "$(ls -A */ 2> /dev/null)" ]; then
        for d in */ ; do
            if [ -d /opt/src/${d} ]; then
                for p in ${d}*.patch; do
                    echo "patch /opt/patches/$p"
                    git -C /opt/src/${d} apply /opt/patches/$p
                done
            fi
        done
    fi
    popd
fi

echo "======== Replacing files ========"
if [ -d ./files ]; then
    pushd files
    if [ ! -z "$(ls -A */ 2> /dev/null)" ]; then
        for d in */ ; do
            pushd $d
            if [ -d /opt/src/${d} ]; then
                for p in $(find . -type f); do
                    if [ -f "/opt/files/$d$p" ]; then
                        echo "Adding $p in /opt/files/$d to /opt/src/${d::-1}/$(dirname $p)"
                        pushd /opt/src/${d::-1}/
                        mkdir -p "$(dirname $p)"
                        cp --force "/opt/files/$d$p" "$(dirname $p)"
                        popd

                    fi
                done
            fi
            if [ -d /opt/deps/${d} ]; then
                for p in $(find . -type f); do
                    if [ -f "/opt/files/$d$p" ]; then
                        echo "Adding $p in /opt/files/$d to /opt/deps/${d::-1}/$(dirname $p)"
                        pushd /opt/deps/${d::-1}/
                        mkdir -p "$(dirname $p)"
                        cp --force "/opt/files/$d$p" "$(dirname $p)"
                        popd

                    fi
                done
            fi
            popd
        done
    fi
    popd
fi

if [[ ! -z ${LOAD_CACHE} ]]; then
    echo "======== Loading cache ========"

    mkdir -p /opt/cache/.dub/
    rsync --info=progress2 -azh /opt/cache/.dub/ ~/.dub/
fi

echo "======== Loading dub dependencies ========"

if [[ ! -z ${DEBUG} ]]; then
    export DFLAGS='-g --d-debug'
fi
export DC='/usr/bin/ldc2'

if [[ ! -z ${NIJIGENERATE} ]]; then
    # Build nijigenerate
    pushd src
    pushd nijigenerate

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
    popd
    popd
fi

if [[ ! -z ${NIJIEXPOSE} ]]; then
    # Build nijiexpose
    pushd src
    pushd nijiexpose

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
    popd
    popd
fi

echo "======== Removing preBuildCommands ========"

pushd ~/.dub/packages/
for d in */ ; do
    di=${d::-1}
    if [ -d ~/.dub/packages/${di} ]; then
        pushd ~/.dub/packages/${di}
        if [ -d */ ]; then
            pushd */

            if [ -d ${di}*/ ]; then
                pushd ${di}*/
                echo "Processing ${di}"
                if [ -f dub.sdl ]; then
                    echo "  Transforming ${di} sdl -> json"
                    dub convert -f json
                fi

                rm -f dub.json.bak*
                mv dub.json dub.json.bak
                jq 'walk(if type == "object" then with_entries(select(.key | test("preBuildCommands*") | not)) else . end)' dub.json.bak > dub.json
                popd
            fi
            popd
        fi
        popd
    fi
done
popd

echo "======== Applying dub lib patches ========"

if [ -d ./patches ]; then
    pushd patches
    if [ ! -z "$(ls -A */ 2> /dev/null)" ]; then
        for d in */ ; do
            if [ -d ~/.dub/packages/${d::-1} ]; then
                for p in ${d}*.patch; do
                    echo "patch /opt/patches/$p"
                    pushd ~/.dub/packages/${d::-1}/*/${d::-1}
                    patch -p1 < /opt/patches/$p
                    popd
                done
            fi
        done
    fi
    popd
fi

echo "======== Replacing dub lib files ========"
if [ -d ./files ]; then
    pushd files
    if [ ! -z "$(ls -A */ 2> /dev/null)" ]; then
        for d in */ ; do
            pushd $d
            if [ -d ~/.dub/packages/${d::-1} ]; then
                for p in $(find . -type f); do
                    if [ -f "/opt/files/$d$p" ]; then
                        echo "Adding $p in /opt/files/$d to ~/.dub/packages/${d::-1}/*/${d::-1}/$(dirname $p)"
                        pushd ~/.dub/packages/${d::-1}/*/${d::-1}/
                        mkdir -p "$(dirname $p)"
                        cp --force "/opt/files/$d$p" "$(dirname $p)"
                        popd
                    fi
                done
            fi
            popd
        done
    fi
    popd
fi

check_dub_i2d_imgui

prepare_i2d_imgui

if [[ ! -z ${NIJIGENERATE} ]]; then
    echo "======== Starting nijigenerate ========"

    # Build nijigenerate
    pushd src
    pushd nijigenerate

cat > ./source/nijigenerate/ver.d <<EOF
module nijigenerate.ver;

enum INC_VERSION = "$(semver /opt/src/nijigenerate/)";
EOF

    # Gen tl files
    chmod +x ./gentl.sh
    ./gentl.sh

    mkdir -p out

    echo "======== Building nijigenerate ========"
    echo "Build time" >> /opt/out/nijigenerate-stats 
    if [[ -z ${LOAD_CACHE} ]]; then
    { time \
        dub build \
            --config=linux-full \
            --cache=user \
            --non-interactive \
                2>&1 ; \
        } 2>> /opt/out/nijigenerate-stats 
    else
        { time \
            dub build \
                --config=linux-full \
                --cache=user \
                --non-interactive \
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

cat > ./source/nijiexpose/ver.d <<EOF
module nijiexpose.ver;

enum INS_VERSION = "$(semver /opt/src/nijiexpose/)";
EOF
    mkdir -p out

    echo "======== Building nijiexpose ========"
    echo "Build time" >> /opt/out/nijiexpose-stats 
    if [[ -z ${LOAD_CACHE} ]]; then
        { time \
            dub build \
                --config=linux-full \
                --cache=user \
                --non-interactive \
                --override-config=facetrack-d/web-adaptors \
                    2>&1 ; \
            } 2>> /opt/out/nijiexpose-stats
    else
        { time \
            dub build \
                --config=linux-full \
                --cache=user \
                --non-interactive \
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

    find /opt/cache/ -mindepth 1 -maxdepth 1 -exec rm -r -- {} +
    mkdir -p /opt/cache/.dub/
    rsync --info=progress2 -azh ~/.dub/ /opt/cache/.dub/

fi

