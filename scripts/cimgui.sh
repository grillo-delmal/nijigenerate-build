#!/usr/bin/bash

function prepare_i2d_imgui() {

if [ -z ${I2D_IMGUI_VERSION} ]; then

echo "======== Checking imgui version ========"

pushd /tmp

I2D_IMGUI_VERSION=$(cat /opt/out/nijigenerate-describe | jq -r '.packages[] | select(.name=="i2d-imgui") | .version')
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

cat > /opt/out/i2d-imgui-state <<EOF
{
    "i2d-imgui": "${I2D_IMGUI_VERSION}",
    "cimgui": "${CIMGUI_COMMIT}",
    "imgui": "${IMGUI_COMMIT}"
}
EOF

popd

fi

if [ ! -f ~/.dub/packages/i2d-imgui*/${I2D_IMGUI_VERSION}/i2d-imgui/deps/cimgui/imgui/imgui.h ]; then
echo "======== Getting imgui submodules ========"

pushd ~/.dub/packages/i2d-imgui*/${I2D_IMGUI_VERSION}/i2d-imgui/

#Prepare i2d-imgui
curl -LO https://github.com/Inochi2D/cimgui/archive/${CIMGUI_COMMIT}/cimgui-${CIMGUI_COMMIT::7}.tar.gz 2> /dev/null
tar -xzf cimgui-${CIMGUI_COMMIT::7}.tar.gz
rm -rf ./deps/cimgui
mv cimgui-${CIMGUI_COMMIT} ./deps/cimgui

curl -LO https://github.com/Inochi2D/imgui/archive/${IMGUI_COMMIT}/imgui-${IMGUI_COMMIT::7}.tar.gz 2> /dev/null

tar -xzf imgui-${IMGUI_COMMIT::7}.tar.gz
rm -rf ./deps/cimgui/imgui
mv imgui-${IMGUI_COMMIT} ./deps/cimgui/imgui

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
mkdir deps/cimgui/.git

popd
fi

if [[ ! -z ${PREBUILD_IMGUI} ]]; then

    echo "======== Prebuild imgui ========"
    pushd ~/.dub/packages/i2d-imgui*/${I2D_IMGUI_VERSION}/i2d-imgui/

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
