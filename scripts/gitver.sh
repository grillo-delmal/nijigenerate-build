#!/usr/bin/bash

function git_version() {
        local DESCRIBE=`git -C $1 describe --tags --exclude nightly --always`
    if [[ "${DESCRIBE}" =~ ^[v] ]]; then
        DESCRIBE="${DESCRIBE:1}"
    fi

    # increment the build number (ie 115 to 116)
    local VERSION=`echo $DESCRIBE | awk '{split($0,a,"-"); print a[1]}'`
    local BUILD=`echo $DESCRIBE | awk '{split($0,a,"-"); print a[2]}'`

    if [[ "${DESCRIBE}" =~ ^[A-Fa-f0-9]+$ ]]; then
        VERSION="0.0.0"
    fi

    if [[ ! "${BUILD}" =~ ^[0-9]+$ ]]; then
        local MODE=${BUILD}
        if [[ "${MODE}" =~ ^pre || "${MODE}" =~ ^rc ]]; then
            echo "${VERSION}~${MODE}"
        elif [ "${BUILD}" = "" ]; then
            echo "${VERSION}"
        else
            echo "${VERSION}_${MODE}"
        fi
        return
    fi

    echo ${VERSION}
}

function git_build() {
        local DESCRIBE=`git -C $1 describe --tags --exclude nightly --always`
    if [[ "${DESCRIBE}" =~ ^[v] ]]; then
        DESCRIBE="${DESCRIBE:1}"
    fi

    # increment the build number (ie 115 to 116)
    local BUILD=`echo $DESCRIBE | awk '{split($0,a,"-"); print a[2]}'`

    if [[ "${DESCRIBE}" =~ ^[A-Fa-f0-9]+$ ]]; then
        BUILD=`git -C $1 rev-list --count HEAD`
    fi

    if [ "${BUILD}" = "" ]; then
        BUILD='0'
    fi

    if [[ ! "${BUILD}" =~ ^[0-9]+$ ]]; then
        BUILD=`echo $DESCRIBE | awk '{split($0,a,"-"); print a[3]}'`
    fi

    if [ "${BUILD}" = "" ]; then
        BUILD='0'
    fi

    echo ${BUILD}
}
