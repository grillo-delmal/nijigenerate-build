#!/usr/bin/bash

function check_local_imgui() {

    [ ! -d /opt/deps/i2d-imgui ] && return

    echo "======== Checking local imgui version ========"
    I2D_IMGUI_VERSION=$(semver /opt/deps/i2d-imgui)
    A=($(git -C /opt/deps/i2d-imgui submodule status deps/cimgui)/ //)
    CIMGUI_COMMIT=${A[0]}
    A=($(git -C /opt/deps/i2d-imgui/deps/cimgui/ submodule status imgui)/ //)
    IMGUI_COMMIT=${A[0]}

    I2D_IMGUI_LIB_PATH=/opt/deps/i2d-imgui

cat > /opt/out/i2d-imgui-state <<EOF
{
    "i2d-imgui": "${I2D_IMGUI_VERSION}",
    "cimgui": "${CIMGUI_COMMIT}",
    "imgui": "${IMGUI_COMMIT}"
}
EOF

}

function check_dub_i2d_imgui() {

    [ -d /opt/deps/i2d-imgui ] && return

    echo "======== Checking remote imgui version ========"

    pushd /tmp

    DESCRIBE_FILE=/opt/out/nijigenerate-describe
    [ ! -f $DESCRIBE_FILE ] && DESCRIBE_FILE=/opt/out/nijiexpose-describe

    I2D_IMGUI_VERSION=$(cat $DESCRIBE_FILE | jq -r '.packages[] | select(.name=="i2d-imgui") | .version')
    git clone -q --depth 1 --branch v${I2D_IMGUI_VERSION} https://github.com/Inochi2D/i2d-imgui 2> /dev/null
    A=($(git -C ./i2d-imgui/ submodule status deps/cimgui)/ //)
    CIMGUI_COMMIT=${A[0]:1}
    mkdir ./cimgui
    git -C ./cimgui init -q
    git -C ./cimgui remote add origin https://github.com/Inochi2D/cimgui.git
    git -C ./cimgui fetch -q --depth 1 origin ${CIMGUI_COMMIT}
    git -C ./cimgui checkout -q FETCH_HEAD 2> /dev/null
    A=($(git -C ./cimgui/ submodule status imgui)/ //)
    IMGUI_COMMIT=${A[0]:1}

    popd

    I2D_IMGUI_LIB_PATH=~/.dub/packages/i2d-imgui/${I2D_IMGUI_VERSION}/i2d-imgui/

cat > /opt/out/i2d-imgui-state <<EOF
{
    "i2d-imgui": "${I2D_IMGUI_VERSION}",
    "cimgui": "${CIMGUI_COMMIT}",
    "imgui": "${IMGUI_COMMIT}"
}
EOF

}

function prepare_i2d_imgui() {

    echo "======== Prepparing i2d-imgui submodules ========"
    pushd ${I2D_IMGUI_LIB_PATH}

    if [ ! -f ./deps/cimgui/cimgui.h ]; then
        #Prepare i2d-imgui
        curl -LO https://github.com/Inochi2D/cimgui/archive/${CIMGUI_COMMIT}/cimgui-${CIMGUI_COMMIT::7}.tar.gz
        tar -xzf cimgui-${CIMGUI_COMMIT::7}.tar.gz
        rm -rf ./deps/cimgui
        mv cimgui-${CIMGUI_COMMIT} ./deps/cimgui

        if [ ! -f ./deps/cimgui/imgui/imgui.h ]; then
            curl -LO https://github.com/Inochi2D/imgui/archive/${IMGUI_COMMIT}/imgui-${IMGUI_COMMIT::7}.tar.gz

            tar -xzf imgui-${IMGUI_COMMIT::7}.tar.gz
            rm -rf ./deps/cimgui/imgui
            mv imgui-${IMGUI_COMMIT} ./deps/cimgui/imgui
        fi
    fi

    rm -rf ./deps/freetype
    rm -rf ./deps/glbinding
    rm -rf ./deps/glfw
    rm -rf ./deps/SDL
    rm -rf ./deps/cimgui/imgui/examples/

    # FIX: Make i2d-imgui submodule checking only check cimgui
    rm .gitmodules
cat > .gitmodules <<EOF
[submodule "deps/cimgui"]
	path = deps/cimgui
	url = https://github.com/Inochi2D/cimgui.git
EOF
    rm -rf deps/cimgui/.git
    mkdir deps/cimgui/.git

    popd

    if [[ ! -z ${PREBUILD_IMGUI} ]]; then

        echo "======== Prebuild imgui ========"
        pushd ${I2D_IMGUI_LIB_PATH}

        # Build i2d-imgui deps
        mkdir -p deps/build_linux_x64_cimguiStatic
        mkdir -p deps/build_linux_x64_cimguiDynamic

        ARCH=$(uname -m)
        if [ "${ARCH}" == 'x86_64' ]; then
            if [[ -z ${DEBUG} ]]; then
                cmake -DSTATIC_CIMGUI= -S deps -B deps/build_linux_x64_cimguiStatic
                cmake --build deps/build_linux_x64_cimguiStatic --config Release

                cmake -S deps -B deps/build_linux_x64_cimguiDynamic
                cmake --build deps/build_linux_x64_cimguiDynamic --config Release
            else
                cmake -DCMAKE_BUILD_TYPE=Debug -DSTATIC_CIMGUI= -S deps -B deps/build_linux_x64_cimguiStatic
                cmake --build deps/build_linux_x64_cimguiStatic --config Debug

                cmake -DCMAKE_BUILD_TYPE=Debug -S deps -B deps/build_linux_x64_cimguiDynamic
                cmake --build deps/build_linux_x64_cimguiDynamic --config Debug
            fi
        elif [ "${ARCH}" == 'aarch64' ]; then
            if [[ -z ${DEBUG} ]]; then
                cmake -DSTATIC_CIMGUI= -S deps -B deps/build_linux_aarch64_cimguiStatic
                cmake --build deps/build_linux_aarch64_cimguiStatic --config Release

                cmake -S deps -B deps/build_linux_aarch64_cimguiDynamic
                cmake --build deps/build_linux_aarch64_cimguiDynamic --config Release
            else
                cmake -DCMAKE_BUILD_TYPE=Debug -DSTATIC_CIMGUI= -S deps -B deps/build_linux_aarch64_cimguiStatic
                cmake --build deps/build_linux_aarch64_cimguiStatic --config Debug

                cmake -DCMAKE_BUILD_TYPE=Debug -S deps -B deps/build_linux_aarch64_cimguiDynamic
                cmake --build deps/build_linux_aarch64_cimguiDynamic --config Debug
            fi
        fi
        PREBUILD_IMGUI=
        popd
    fi

}
