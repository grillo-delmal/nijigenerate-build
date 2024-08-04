#!/usr/bin/bash

function semver() {
    local DESCRIBE=`git -C $1 describe --tags --exclude nightly --always`
    if [[ "${DESCRIBE}" =~ ^[v] ]]; then
        DESCRIBE="${DESCRIBE:1}"
    fi

    # increment the build number (ie 115 to 116)
    local VERSION=`echo $DESCRIBE | awk '{split($0,a,"-"); print a[1]}'`
    local BUILD=`echo $DESCRIBE | awk '{split($0,a,"-"); print a[2]}'`
    local PATCH=`echo $DESCRIBE | awk '{split($0,a,"-"); print a[3]}'`
    local MODE=

    if [[ "${DESCRIBE}" =~ ^[A-Fa-f0-9]+$ ]]; then
        VERSION="0.0.0"
        BUILD=`git -C $1 rev-list --count HEAD`
        PATCH=${DESCRIBE}
    fi

    if [ "${BUILD}" = "" ]; then
        BUILD='0'
        if [ ! -z "$2" ]; then
            echo ${2}+build.0-og.${VERSION}
            return
        fi
        echo ${VERSION}
        return
    fi

    if [[ ! "${BUILD}" =~ ^[0-9]+$ ]]; then
        MODE=`echo $DESCRIBE | awk '{split($0,a,"-"); print a[2]}'`
        BUILD=`echo $DESCRIBE | awk '{split($0,a,"-"); print a[3]}'`
        PATCH=`echo $DESCRIBE | awk '{split($0,a,"-"); print a[4]}'`

        if [ "${BUILD}" = "" ]; then

            if [[ "${MODE}" =~ ^pre || "${MODE}" =~ ^rc ]]; then
                RESULT="${VERSION}-${MODE}"
            else
                RESULT="${VERSION}+${MODE}"
            fi

            if [ ! -z "$2" ]; then
                echo ${2}+build.0-og.${RESULT}
            else
                echo ${RESULT}
            fi

        else
            if [[ "${MODE}" =~ ^pre || "${MODE}" =~ ^rc ]]; then
                RESULT="${VERSION}-${MODE}"
            else
                RESULT="${VERSION}+${MODE}"
            fi

            if [ ! -z "$2" ]; then
                echo ${2}+build.0-og.${RESULT}.build.${BUILD}.${PATCH}
            else
                echo ${RESULT}.build.${BUILD}.${PATCH}
            fi
        fi
        return
    fi

    if [ "${BUILD}" = "" ]; then
        PATCH=$DESCRIBE
    fi

    if [ ! -z "$2" ]; then
        echo ${2}+build.0-og.${VERSION}.build.${BUILD}.${PATCH}
        return
    fi

    echo ${VERSION}+build.${BUILD}.${PATCH}
}