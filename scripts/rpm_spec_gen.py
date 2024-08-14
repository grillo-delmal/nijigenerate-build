#!/usr/bin/python3

import json
import subprocess
import shutil
import math

from pathlib import Path
from spec_gen_util import LibData, LibSpecFile

removed_deps = ['openssl-static']

def find_deps(parent, dep_graph):
    deps = set(dep_graph[parent]['dependencies'])
    for name in dep_graph[parent]['dependencies']:
        deps = deps.union(find_deps(name, dep_graph))
    return deps

data = {}
with open("build_out/nijigenerate-describe") as f:
    data = json.load(f)

nijigenerate_dep_graph = {
    package['name']: package 
        for package in data['packages'] if package['name'] not in removed_deps }
for name in nijigenerate_dep_graph.keys():
    nijigenerate_dep_graph[name]['dependencies'] = [dep for dep in nijigenerate_dep_graph[name]['dependencies'] if dep not in removed_deps]

nijigenerate_deps = list(find_deps("nijigenerate", nijigenerate_dep_graph))
nijigenerate_deps.sort()
print("All nijigenerate deps", nijigenerate_deps)

data = {}
with open("build_out/nijiexpose-describe") as f:
    data = json.load(f)

nijiexpose_dep_graph = {
    package['name']: package 
        for package in data['packages'] if package['name'] not in removed_deps }
for name in nijiexpose_dep_graph.keys():
    nijiexpose_dep_graph[name]['dependencies'] = [dep for dep in nijiexpose_dep_graph[name]['dependencies'] if dep not in removed_deps]

nijiexpose_deps = list(find_deps("nijiexpose", nijiexpose_dep_graph))
nijiexpose_deps.sort()
print("All nijiexpose deps", nijiexpose_deps)

# Find nijigenerate libs
nijigenerate_project_libs = []
project_deps = {
    name: nijigenerate_dep_graph[name] 
        for name in nijigenerate_dep_graph.keys() 
        if nijigenerate_dep_graph[name]['path'].startswith(
            '/opt/deps/') and \
        name in nijigenerate_deps}

nijigenerate_pd_names = list(project_deps.keys())
nijigenerate_pd_names.sort()
print("Direct nijigenerate deps found", nijigenerate_pd_names)

for name in nijigenerate_pd_names:
    NAME = project_deps[name]['name'].replace('-', '_').lower()
    SEMVER = project_deps[name]['version']
    GITPATH = project_deps[name]['path'].replace("/opt/deps","./src")
    COMMIT = subprocess.run(
        ['git', '-C', GITPATH, 'rev-parse', 'HEAD'],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    GITVER = subprocess.run(
        ['bash', '-c', 
            'source ./scripts/gitver.sh;' + \
            'git_version ' + GITPATH],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    GITDIST = subprocess.run(
        ['bash', '-c', 
            'source ./scripts/gitver.sh;' + \
            'git_build ' + GITPATH],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    SOURCE_BASE_URL= subprocess.run(
        ['git', '-C', GITPATH, 'config', '--get', 'remote.origin.url'],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    if SOURCE_BASE_URL[-4:] == ".git":
        SOURCE_BASE_URL = SOURCE_BASE_URL[:-4]

    extra_consts={}

    if name == "i2d-imgui":
        imgui_data = {}
        with open("build_out/i2d-imgui-state") as f:
            imgui_data = json.load(f)

        extra_consts={
            "cimgui_commit":imgui_data["cimgui"],
            "cimgui_short":imgui_data["cimgui"][:7],
            "imgui_commit":imgui_data["imgui"],
            "imgui_short":imgui_data["imgui"][:7]
        }

    nijigenerate_project_libs.append(
        LibData(
            name, 
            list(
                { 
                    dep.split(':')[0] 
                        for dep in project_deps[name]['dependencies']
                }), 
            GITVER,
            SEMVER, 
            GITDIST,
            COMMIT,
            SOURCE_BASE_URL + ("/archive/%%{%s_commit}/%s-%%{%s_short}.tar.gz" % (NAME, NAME, NAME)),
            extra_consts=extra_consts)            
        )

# Find nijiexpose libs
nijiexpose_project_libs = []
project_deps = {
    name: nijiexpose_dep_graph[name] 
        for name in nijiexpose_dep_graph.keys() 
        if nijiexpose_dep_graph[name]['path'].startswith(
            '/opt/deps/') and \
        name in nijiexpose_deps}

nijiexpose_pd_names = list(project_deps.keys())
nijiexpose_pd_names.sort()
print("Direct nijiexpose deps found", nijiexpose_pd_names)

for name in nijiexpose_pd_names:
    NAME = project_deps[name]['name'].replace('-', '_').lower()
    SEMVER = project_deps[name]['version']
    GITPATH = project_deps[name]['path'].replace("/opt/deps","./src")
    COMMIT = subprocess.run(
        ['git', '-C', GITPATH, 'rev-parse', 'HEAD'],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    GITVER = subprocess.run(
        ['bash', '-c', 
            'source ./scripts/gitver.sh;' + \
            'git_version ' + GITPATH],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    GITDIST = subprocess.run(
        ['bash', '-c', 
            'source ./scripts/gitver.sh;' + \
            'git_build ' + GITPATH],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    SOURCE_BASE_URL= subprocess.run(
        ['git', '-C', GITPATH, 'config', '--get', 'remote.origin.url'],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    if SOURCE_BASE_URL[-4:] == ".git":
        SOURCE_BASE_URL = SOURCE_BASE_URL[:-4]

    extra_consts={}

    if name == "i2d-imgui":
        imgui_data = {}
        with open("build_out/i2d-imgui-state") as f:
            imgui_data = json.load(f)

        extra_consts={
            "cimgui_commit":imgui_data["cimgui"],
            "cimgui_short":imgui_data["cimgui"][:7],
            "imgui_commit":imgui_data["imgui"],
            "imgui_short":imgui_data["imgui"][:7]
        }

    nijiexpose_project_libs.append(
        LibData(
            name, 
            list(
                { 
                    dep.split(':')[0] 
                        for dep in project_deps[name]['dependencies']
                }), 
            GITVER,
            SEMVER, 
            GITDIST,
            COMMIT,
            SOURCE_BASE_URL + ("/archive/%%{%s_commit}/%s-%%{%s_short}.tar.gz" % (NAME, NAME, NAME)),
            extra_consts=extra_consts)            
        )

# Find indirect nijigenerate deps
indirect_deps = {
    name: nijigenerate_dep_graph[name] 
        for name in nijigenerate_dep_graph.keys() 
        if not nijigenerate_dep_graph[name]['path'].startswith(
            '/opt/deps/') and \
        name in nijigenerate_deps}

id_names = list(indirect_deps.keys())
id_names.sort()
print("Indirect nijigenerate deps found", id_names)
for id_name in id_names:
    print("  %s: %s" % (id_name, indirect_deps[id_name]["dependencies"]))

nijigenerate_true_deps = {}
nijigenerate_true_names = []

for name in id_names:
    NAME = indirect_deps[name]['name'].lower()
    TRUENAME = NAME.split(":")[0]
    SEMVER = indirect_deps[name]['version']

    if TRUENAME in nijigenerate_true_deps:
        nijigenerate_true_deps[TRUENAME].append({"name": NAME, "semver":SEMVER})
    else:
        nijigenerate_true_deps[TRUENAME] = [{"name": NAME, "semver":SEMVER}]
        nijigenerate_true_names.append(TRUENAME)

nijigenerate_true_names.sort()

# Find indirect nijiexpose deps
indirect_deps = {
    name: nijiexpose_dep_graph[name] 
        for name in nijiexpose_dep_graph.keys() 
        if not nijiexpose_dep_graph[name]['path'].startswith(
            '/opt/deps/') and \
        name in nijiexpose_deps}

id_names = list(indirect_deps.keys())
id_names.sort()
print("Indirect nijiexpose deps found", id_names)
for id_name in id_names:
    print("  %s: %s" % (id_name, indirect_deps[id_name]["dependencies"]))

nijiexpose_true_deps = {}
nijiexpose_true_names = []

for name in id_names:
    NAME = indirect_deps[name]['name'].lower()
    TRUENAME = NAME.split(":")[0]
    SEMVER = indirect_deps[name]['version']

    if TRUENAME in nijiexpose_true_deps:
        nijiexpose_true_deps[TRUENAME].append({"name": NAME, "semver":SEMVER})
    else:
        nijiexpose_true_deps[TRUENAME] = [{"name": NAME, "semver":SEMVER}]
        nijiexpose_true_names.append(TRUENAME)

nijiexpose_true_names.sort()

true_names = list(set(nijigenerate_true_names + nijiexpose_true_names))
true_names.sort()

nijigenerate_indirect_libs = []
nijiexpose_indirect_libs = []

for name in true_names:

    # Copy build files into destination folder
    Path("build_out/rpms/zdub-deps/zdub-%s"  % name).mkdir(parents=True, exist_ok=True)
    for file in Path("files/%s" % name).glob("**/*"):
        if file.is_file():
            shutil.copy(file, "build_out/rpms/zdub-deps/zdub-%s/" % name)

    # Also copy patches
    for file in Path("patches/%s" % name).glob("*.patch"):
        shutil.copy(file, "build_out/rpms/zdub-deps/zdub-%s/" % name)

    id_deps = set()
    SEMVER = None

    if name in nijigenerate_true_names:
        # Find nijigenerate lib dependencies
        SEMVER = nijigenerate_true_deps[name][0]["semver"]

        for dep in nijigenerate_true_deps[name]:
            id_deps = id_deps.union(set(nijigenerate_dep_graph[dep["name"]]['dependencies']))
            SEMVER = dep["semver"]

    if name in nijiexpose_true_names:
        # Find nijiexpose lib dependencies
        SEMVER = nijiexpose_true_deps[name][0]["semver"]

        for dep in nijiexpose_true_deps[name]:
            id_deps = id_deps.union(set(nijiexpose_dep_graph[dep["name"]]['dependencies']))
            if SEMVER is None:
                SEMVER = dep["semver"]
            elif SEMVER != dep["semver"]:
                print("WARNING!!!: Dependency inconsistency %s %s" % (SEMVER, dep["semver"]))

    for dep in list(id_deps):
        dep_truename = dep.split(":")[0]
        if dep_truename != dep:
            id_deps.remove(dep)
            if dep_truename != name:
                id_deps.add(dep_truename)
    
    # Write specfile
    extra_consts={}

    if name == "i2d-imgui":
        imgui_data = {}
        with open("build_out/i2d-imgui-state") as f:
            imgui_data = json.load(f)

        extra_consts={
            "cimgui_commit":imgui_data["cimgui"],
            "cimgui_short":imgui_data["cimgui"][:7],
            "imgui_commit":imgui_data["imgui"],
            "imgui_short":imgui_data["imgui"][:7]
        }

    lib_spec = LibSpecFile(
        name, 
        list(
            { 
                dep.split(':')[0] 
                    for dep in list(id_deps)
            }), 
        SEMVER,
        extra_consts=extra_consts)

    lib_spec.spec_gen(
                "build_out/rpms/zdub-deps/zdub-%s/zdub-%s.spec" % (name, name))

    if name in nijigenerate_true_names:
        nijigenerate_indirect_libs.append(lib_spec)

    if name in nijiexpose_true_names:
        nijiexpose_indirect_libs.append(lib_spec)

# Write nijigenerate.spec
Path("build_out/rpms/nijigenerate-rpm/").mkdir(parents=True, exist_ok=True)
with open("build_out/rpms/nijigenerate-rpm/nijigenerate.spec", 'w') as spec:

    # Copy nijigenerate files and patches patches
    for file in Path("files/%s" % "nijigenerate").glob("**/*"):
        if file.is_file():
            shutil.copy(file, "build_out/rpms/nijigenerate-rpm/")
    for file in Path("patches/%s" % "nijigenerate").glob("*.patch"):
        if file.is_file():
            shutil.copy(file, "build_out/rpms/nijigenerate-rpm/")

    # Copy nijigenerate files and patches patches
    for lib in nijigenerate_project_libs:
        for file in Path("files/%s" % lib.name).glob("**/*"):
            if file.is_file():
                shutil.copy(file, "build_out/rpms/nijigenerate-rpm/")
        for file in Path("patches/%s" % lib.name).glob("*.patch"):
            if file.is_file():
                shutil.copy(file, "build_out/rpms/nijigenerate-rpm/")

    # CONSTS
    SEMVER = subprocess.run(
        ['bash', '-c', 
            'source ./scripts/semver.sh;' + \
            'semver ./src/nijigenerate'],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    COMMIT = subprocess.run(
        'git -C ./src/nijigenerate rev-parse HEAD'.split(),
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    GITVER = subprocess.run(
        ['bash', '-c', 
            'source ./scripts/gitver.sh;' + \
            'git_version ./src/nijigenerate'],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    GITDIST = subprocess.run(
        ['bash', '-c', 
            'source ./scripts/gitver.sh;' + \
            'git_build ./src/nijigenerate'],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

    spec.write('\n'.join([
        "%%define nijigenerate_ver %s" % GITVER,
        "%%define nijigenerate_semver %s" % SEMVER,
        "%%define nijigenerate_dist %s" % GITDIST,
        "%%define nijigenerate_commit %s" % COMMIT,
        "%%define nijigenerate_short %s" % COMMIT[:7],
        "",
        ""]))

    if len(nijigenerate_project_libs) > 0:
        spec.write('\n'.join([
            '# Project maintained deps',
            ""]))

        for lib in nijigenerate_project_libs:
            NAME = lib.name.replace('-', '_').lower()

            spec.write('\n'.join([
                "%%define %s_semver %s" % (NAME, lib.semver),
                "%%define %s_commit %s" % (NAME, lib.commit),
                "%%define %s_short %s" % (NAME, lib.commit[:7]),
                ""]))

            for key in lib.extra_consts.keys():
                spec.write('\n'.join([
                    "%%define %s%s %s" % (
                        key,
                        " " * (13-len(key)),
                        lib.extra_consts[key]) ,
                    ""
                ]))
            spec.write('\n')

    # WRITING HEAD
    spec.write('\n'.join([line[8:] for line in '''\
        %if 0%{nijigenerate_dist} > 0
        %define nijigenerate_suffix ^%{nijigenerate_dist}.git%{nijigenerate_short}
        %endif

        Name:           nijigenerate
        Version:        %{nijigenerate_ver}%{?nijigenerate_suffix:}
        Release:        %autorelease
        Summary:        Tool to create and edit nijilive puppets

        '''.splitlines()]))

    # LICENSES

    # List direct licenses
    spec.write('\n'.join([
        "# Bundled lib licenses",
        ""]))        
    spec.write('\n'.join([
        "##   %s licenses: %s" % (
            lib.name, 
            ' and '.join(lib.licenses)
            ) for lib in nijigenerate_project_libs]))
    spec.write('\n')

    # List static dependency licenses
    spec.write('\n'.join([
        "# Static dependencies licenses",
        ""]))        
    spec.write('\n'.join([
        "##   %s licenses: %s" % (
            lib.name, 
            ' and '.join(lib.licenses)
        ) for lib in nijigenerate_indirect_libs]))
    spec.write('\n')

    # Add license field

    licenses = list(set().union(
        *[lib.licenses for lib in nijigenerate_project_libs],
        *[lib.licenses for lib in nijigenerate_indirect_libs]))
    licenses.sort()
    licenses.remove("BSD-2-Clause")
    licenses.insert(0, "BSD-2-Clause")
    
    spec.write('\n'.join([
        "License:        %s" % ' and '.join(licenses),
        "",
        ""]))

    spec.write('\n'.join([line[8:] for line in '''\
        URL:            https://github.com/grillo-delmal/nijigenerate-rpm

        #https://github.com/nijigenerate/nijigenerate/archive/{nijigenerate_commit}/{name}-{nijigenerate_short}.tar.gz
        Source0:        %{name}-%{version}-norestricted.tar.gz
        Source1:        config.d
        Source2:        icon.png
    
        '''.splitlines()]))

    # OTHER SOURCES
    spec.write('\n'.join([
        "# Project maintained deps",
        ""]))

    src_cnt = 3

    for lib in nijigenerate_project_libs:
        spec.write('\n'.join([
            "Source%d:%s%s" % (
                src_cnt, 
                " " * (8 - math.floor(math.log10(src_cnt) if src_cnt > 0 else 0)), 
                lib.source) ,
            ""
        ]))
        src_cnt += 1
        for src in lib.ex_sources:
            spec.write('\n'.join([
                "Source%d:%s%s" % (
                    src_cnt, 
                    " " * (8 - math.floor(math.log10(src_cnt))), 
                    src) ,
                ""
            ]))
            src_cnt += 1
        if len(lib.file_sources) > 0:
            for src in lib.file_sources:
                spec.write('\n'.join([
                    "Source%d:%s%s" % (
                        src_cnt, 
                        " " * (8 - math.floor(math.log10(src_cnt))), 
                        src["name"]) ,
                    ""
                ]))
            src_cnt += 1
    spec.write('\n')

    # PATCHES
    ptch_cnt = 0

    patch_list = []
    if Path("patches/%s" % "nijigenerate").exists():
        patch_list = list(Path("patches/%s" % "nijigenerate").glob("*.patch"))
        patch_list.sort()
    for file in patch_list:
        spec.write('\n'.join([
            "Patch%d:%s%s" % (
                ptch_cnt, 
                " " * (9 - math.floor(math.log10(ptch_cnt) if ptch_cnt > 0 else 0)), 
                file.name) ,
            ""
        ]))
        ptch_cnt += 1

    # OTHER PATCHES
    for lib in nijigenerate_project_libs:
        for patch in lib.patches:
            spec.write('\n'.join([
                "Patch%d:%s%s" % (
                    ptch_cnt, 
                    " " * (9 - math.floor(math.log10(ptch_cnt) if ptch_cnt > 0 else 0)), 
                    patch) ,
                ""
            ]))
            ptch_cnt += 1
    spec.write('\n')

    # DEPS

    spec.write('\n'.join([line[8:] for line in '''\
        # dlang
        BuildRequires:  ldc
        BuildRequires:  dub
        BuildRequires:  jq

        BuildRequires:  desktop-file-utils
        BuildRequires:  libappstream-glib
        BuildRequires:  git

        BuildRequires:  zdub-dub-settings-hack

        '''.splitlines()]))

    spec.write('\n'.join([
        "BuildRequires:  zdub-%s-static" % lib.name \
            for lib in nijigenerate_indirect_libs]))

    spec.write('\n')
    spec.write('\n')

    if "i2d-imgui" not in nijigenerate_pd_names:
        spec.write('\n'.join([line[12:] for line in '''\
            # static i2d-imgui reqs
            BuildRequires:  gcc-c++
            BuildRequires:  freetype-devel
            BuildRequires:  SDL2-devel

            '''.splitlines()]))

    for lib in nijigenerate_project_libs:

        if len(lib.build_reqs) > 0:
            spec.write('\n'.join([
                "#%s deps" % lib.name ,
                ""
            ]))
            for build_req in lib.build_reqs:
                spec.write('\n'.join([
                    "BuildRequires:  %s" % build_req ,
                    ""
                ]))
            spec.write('\n')

    spec.write('\n'.join([
        "Requires:       hicolor-icon-theme",
        ""]))
    spec.write('\n')

    for lib in nijigenerate_project_libs:
        if len(lib.requires) > 0:
            spec.write('\n'.join([
                "#%s deps" % lib.name ,
                ""
            ]))
            for req in lib.requires:
                spec.write('\n'.join([
                    "Requires:       %s" % req ,
                    ""
                ]))
            spec.write('\n')

    for lib in nijigenerate_indirect_libs:
        if len(lib.requires) > 0:
            spec.write('\n'.join([
                "#%s deps" % lib.name ,
                ""
            ]))
            for req in lib.requires:
                spec.write('\n'.join([
                    "Requires:       %s" % req ,
                    ""
                ]))
            spec.write('\n')
    spec.write('\n')

    spec.write('\n'.join([line[8:] for line in '''\
        %description
        nijilive is a framework for realtime 2D puppet animation which can be used for VTubing, 
        game development and digital animation. 
        nijigenerate is a tool that lets you create and edit nijilive puppets.
        This is an unbranded build, unsupported by the official project.


        '''.splitlines()]))

    # PREP
    spec.write('\n'.join([line[8:] for line in '''\
        %prep
        %setup -n %{name}-%{nijigenerate_commit}

        '''.splitlines()]))

    # GENERIC FIXES
    spec.write('\n'.join([line[8:] for line in '''\
        # FIX: Nijigenerate version dependent on git
        cat > source/nijigenerate/ver.d <<EOF
        module nijigenerate.ver;

        enum INC_VERSION = "%{nijigenerate_semver}";
        EOF

        # FIX: Add fake dependency
        mkdir -p deps/vibe-d
        cat > deps/vibe-d/dub.sdl <<EOF
        name "vibe-d"
        subpackage "http"
        EOF
        dub add-local deps/vibe-d "0.9.5"

        '''.splitlines()]))

    src_cnt = 3
    ptch_cnt = 0

    patch_list = []
    if Path("patches/%s" % "nijigenerate").exists():
        patch_list = list(Path("patches/%s" % "nijigenerate").glob("*.patch"))
        patch_list.sort()
    for file in patch_list:
        spec.write('\n'.join([
            "%%patch -P %d -p1 -b .%s-%s" % (
                ptch_cnt,
                *list(file.name[:-6].split("_")[0::2])),
            ""
        ]))
        ptch_cnt += 1

    # PREP DEPS
    spec.write('\n'.join([line[8:] for line in '''\
        mkdir -p deps

        # Project maintained deps
        '''.splitlines()]))

    for lib in nijigenerate_project_libs:
        spec.write('\n'.join([
            "tar -xzf %%{SOURCE%d}" % src_cnt,
            "mv %s deps/%s" % (
                lib.prep_file, lib.name), 
            "dub add-local deps/%s/ \"%%{%s_semver}\"" % (
                lib.name, lib.name.replace('-', '_').lower()),
            ""
        ]))
        src_cnt += 1

        spec.write('\n')
        spec.write('\n'.join([
            "pushd deps; pushd %s" % lib.name,
            ""
            ]))
        if len(lib.patches) > 0:
            spec.write('\n')
            for patch in lib.patches:
                spec.write('\n'.join([
                    "%%patch -P %d -p1 -b .%s-%s" % (
                        ptch_cnt,
                        *list(patch[:-6].split("_")[0::2])),
                    ""
                ]))
                ptch_cnt += 1

        if len(lib.file_sources) > 0:
            spec.write("\n")
            for i in range(len(lib.file_sources)):
                if lib.file_sources[i]["path"] != ".":
                    spec.write('\n'.join([
                        "mkdir -p ./%s" % lib.file_sources[i]["path"],
                        "cp --force %%{SOURCE%d} ./%s/" % (src_cnt, lib.file_sources[i]["path"]),
                        ""
                    ]))
                else:
                    spec.write('\n'.join([
                        "cp %%{SOURCE%d} ." % (src_cnt),
                        ""
                    ]))
                src_cnt += 1

        if len(lib.prep) > 0:
            prep = '\n'.join(lib.prep)
            c = 1
            while prep.find("%%{SOURCE%d}" % c) > 0:
                prep = prep.replace("%%{SOURCE%d}" % c, "%%{SOURCE%d}" % src_cnt)
                src_cnt += 1
                c += 1

            spec.write("\n")
            spec.write(prep)


        spec.write('\n'.join([
            "",
            "[ -f dub.sdl ] && dub convert -f json",
            "mv -f dub.json dub.json.base",
            "jq 'walk(if type == \"object\" then with_entries(select(.key | test(\"preBuildCommands*\") | not)) else . end)' dub.json.base > dub.json",
            ""
        ]))

        spec.write('\n'.join([
            "",
            "popd; popd",
            ""
            ]))

        spec.write('\n')

    spec.write('\n')

    # BUILD
    spec.write('\n'.join([line[8:] for line in '''\
        %build
        export DFLAGS="%{_d_optflags}"
        dub build \\
            --cache=local \\
            --config=linux-full \\
            --skip-registry=all \\
            --non-interactive \\
            --temp-build \\
            --compiler=ldc2
        mkdir ./out/
        cp /tmp/.dub/build/nijigenerate*/linux-full*/* ./out/


        '''.splitlines()]))

    # INSTALL

    spec.write('\n'.join([line[8:] for line in '''\
        %install
        install -d ${RPM_BUILD_ROOT}%{_bindir}
        install -p ./out/nijigenerate ${RPM_BUILD_ROOT}%{_bindir}/nijigenerate

        install -d ${RPM_BUILD_ROOT}%{_datadir}/applications/
        install -p -m 644 ./build-aux/linux/nijigenerate.desktop ${RPM_BUILD_ROOT}%{_datadir}/applications/nijigenerate.desktop
        desktop-file-validate \\
            ${RPM_BUILD_ROOT}%{_datadir}/applications/nijigenerate.desktop

        install -d ${RPM_BUILD_ROOT}%{_metainfodir}/
        install -p -m 644 ./build-aux/linux/nijigenerate.appdata.xml ${RPM_BUILD_ROOT}%{_metainfodir}/nijigenerate.appdata.xml
        appstream-util validate-relax --nonet \\
            ${RPM_BUILD_ROOT}%{_metainfodir}/nijigenerate.appdata.xml

        install -d $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/256x256/apps/
        install -p -m 644 %{SOURCE2} $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/256x256/apps/nijigenerate.png

        '''.splitlines()]))
    
    # INSTALL LICENSES
    spec.write('\n'.join([line[8:] for line in '''\
        # Dependency licenses
        install -d ${RPM_BUILD_ROOT}%{_datadir}/licenses/%{name}/deps/
        find ./deps/ -mindepth 1 -maxdepth 1 -exec \\
            install -d ${RPM_BUILD_ROOT}%{_datadir}/licenses/%{name}/{} ';'

        find ./deps/ -mindepth 2 -maxdepth 2 -iname '*LICENSE*' -exec \\
            install -p -m 644 "{}" "${RPM_BUILD_ROOT}%{_datadir}/licenses/%{name}/{}" ';'

        install -d ${RPM_BUILD_ROOT}%{_datadir}/licenses/%{name}/res/
        find ./res/ -mindepth 1 -maxdepth 1 -iname '*LICENSE*' -exec \\
            install -p -m 644 {} ${RPM_BUILD_ROOT}%{_datadir}/licenses/%{name}/{} ';'


        '''.splitlines()]))

    # FILES
    spec.write('\n'.join([line[8:] for line in '''\
        %files
        %license LICENSE
        %{_datadir}/licenses/%{name}/*
        %{_bindir}/nijigenerate
        %{_metainfodir}/nijigenerate.appdata.xml
        %{_datadir}/applications/nijigenerate.desktop
        %{_datadir}/icons/hicolor/256x256/apps/nijigenerate.png


        %changelog
        %autochangelog
        '''.splitlines()][:-1]))

# Write nijiexpose.spec
Path("build_out/rpms/nijiexpose-rpm/").mkdir(parents=True, exist_ok=True)
with open("build_out/rpms/nijiexpose-rpm/nijiexpose.spec", 'w') as spec:

    # Copy nijiexpose files and patches patches
    for file in Path("files/%s" % "nijiexpose").glob("**/*"):
        if file.is_file():
            shutil.copy(file, "build_out/rpms/nijiexpose-rpm/")
    for file in Path("patches/%s" % "nijiexpose").glob("*.patch"):
        if file.is_file():
            shutil.copy(file, "build_out/rpms/nijiexpose-rpm/")

    # Copy nijiexpose files and patches patches
    for lib in nijiexpose_project_libs:
        for file in Path("files/%s" % lib.name).glob("**/*"):
            if file.is_file():
                shutil.copy(file, "build_out/rpms/nijiexpose-rpm/")
        for file in Path("patches/%s" % lib.name).glob("*.patch"):
            if file.is_file():
                shutil.copy(file, "build_out/rpms/nijiexpose-rpm/")

    # CONSTS
    SEMVER = subprocess.run(
        ['bash', '-c', 
            'source ./scripts/semver.sh;' + \
            'semver ./src/nijiexpose'],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    COMMIT = subprocess.run(
        'git -C ./src/nijiexpose rev-parse HEAD'.split(),
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    GITVER = subprocess.run(
        ['bash', '-c', 
            'source ./scripts/gitver.sh;' + \
            'git_version ./src/nijiexpose'],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    GITDIST = subprocess.run(
        ['bash', '-c', 
            'source ./scripts/gitver.sh;' + \
            'git_build ./src/nijiexpose'],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

    spec.write('\n'.join([
        "%%define nijiexpose_ver %s" % GITVER,
        "%%define nijiexpose_semver %s" % SEMVER,
        "%%define nijiexpose_dist %s" % GITDIST,
        "%%define nijiexpose_commit %s" % COMMIT,
        "%%define nijiexpose_short %s" % COMMIT[:7],
        "",
        ""]))

    if len(nijiexpose_project_libs) > 0:
        spec.write('\n'.join([
            '# Project maintained deps',
            ""]))

        for lib in nijiexpose_project_libs:
            NAME = lib.name.replace('-', '_').lower()

            spec.write('\n'.join([
                "%%define %s_semver %s" % (NAME, lib.semver),
                "%%define %s_commit %s" % (NAME, lib.commit),
                "%%define %s_short %s" % (NAME, lib.commit[:7]),
                ""]))

            for key in lib.extra_consts.keys():
                spec.write('\n'.join([
                    "%%define %s%s %s" % (
                        key,
                        " " * (13-len(key)),
                        lib.extra_consts[key]) ,
                    ""
                ]))
            spec.write('\n')

    # WRITING HEAD
    spec.write('\n'.join([line[8:] for line in '''\
        %if 0%{nijiexpose_dist} > 0
        %define nijiexpose_suffix ^%{nijiexpose_dist}.git%{nijiexpose_short}
        %endif

        Name:           nijiexpose
        Version:        %{nijiexpose_ver}%{?nijiexpose_suffix:}
        Release:        %autorelease
        Summary:        Tool to use nijilive puppets

        '''.splitlines()]))

    # LICENSES

    # List direct licenses
    spec.write('\n'.join([
        "# Bundled lib licenses",
        ""]))        
    spec.write('\n'.join([
        "##   %s licenses: %s" % (
            lib.name, 
            ' and '.join(lib.licenses)
            ) for lib in nijiexpose_project_libs]))
    spec.write('\n')

    # List static dependency licenses
    spec.write('\n'.join([
        "# Static dependencies licenses",
        ""]))        
    spec.write('\n'.join([
        "##   %s licenses: %s" % (
            lib.name, 
            ' and '.join(lib.licenses)
        ) for lib in nijiexpose_indirect_libs]))
    spec.write('\n')

    # Add license field

    licenses = list(set().union(
        *[lib.licenses for lib in nijiexpose_project_libs],
        *[lib.licenses for lib in nijiexpose_indirect_libs]))
    licenses.sort()
    licenses.remove("BSD-2-Clause")
    licenses.insert(0, "BSD-2-Clause")
    
    spec.write('\n'.join([
        "License:        %s" % ' and '.join(licenses),
        "",
        ""]))

    spec.write('\n'.join([line[8:] for line in '''\
        URL:            https://github.com/grillo-delmal/nijiexpose-rpm

        #https://github.com/nijigenerate/nijiexpose/archive/{nijiexpose_commit}/{name}-{nijiexpose_short}.tar.gz
        Source0:        %{name}-%{version}-norestricted.tar.gz
        Source1:        icon.png
    
        '''.splitlines()]))

    # OTHER SOURCES
    spec.write('\n'.join([
        "# Project maintained deps",
        ""]))

    src_cnt = 2

    for lib in nijiexpose_project_libs:
        spec.write('\n'.join([
            "Source%d:%s%s" % (
                src_cnt, 
                " " * (8 - math.floor(math.log10(src_cnt) if src_cnt > 0 else 0)), 
                lib.source) ,
            ""
        ]))
        src_cnt += 1
        for src in lib.ex_sources:
            spec.write('\n'.join([
                "Source%d:%s%s" % (
                    src_cnt, 
                    " " * (8 - math.floor(math.log10(src_cnt))), 
                    src) ,
                ""
            ]))
            src_cnt += 1
        if len(lib.file_sources) > 0:
            for src in lib.file_sources:
                spec.write('\n'.join([
                    "Source%d:%s%s" % (
                        src_cnt, 
                        " " * (8 - math.floor(math.log10(src_cnt))), 
                        src["name"]) ,
                    ""
                ]))
            src_cnt += 1
    spec.write('\n')

    # PATCHES
    ptch_cnt = 0

    patch_list = []
    if Path("patches/%s" % "nijiexpose").exists():
        patch_list = list(Path("patches/%s" % "nijiexpose").glob("*.patch"))
        patch_list.sort()
    for file in patch_list:
        spec.write('\n'.join([
            "Patch%d:%s%s" % (
                ptch_cnt, 
                " " * (9 - math.floor(math.log10(ptch_cnt) if ptch_cnt > 0 else 0)), 
                file.name) ,
            ""
        ]))
        ptch_cnt += 1

    # OTHER PATCHES
    for lib in nijiexpose_project_libs:
        for patch in lib.patches:
            spec.write('\n'.join([
                "Patch%d:%s%s" % (
                    ptch_cnt, 
                    " " * (9 - math.floor(math.log10(ptch_cnt) if ptch_cnt > 0 else 0)), 
                    patch) ,
                ""
            ]))
            ptch_cnt += 1
    spec.write('\n')

    # DEPS

    spec.write('\n'.join([line[8:] for line in '''\
        # dlang
        BuildRequires:  ldc
        BuildRequires:  dub
        BuildRequires:  jq

        BuildRequires:  desktop-file-utils
        BuildRequires:  libappstream-glib
        BuildRequires:  git

        BuildRequires:  zdub-dub-settings-hack
        
        '''.splitlines()]))

    spec.write('\n'.join([
        "BuildRequires:  zdub-%s-static" % lib.name \
            for lib in nijiexpose_indirect_libs]))

    spec.write('\n')
    spec.write('\n')
    for lib in nijiexpose_project_libs:

        if len(lib.build_reqs) > 0:
            spec.write('\n'.join([
                "#%s deps" % lib.name ,
                ""
            ]))
            for build_req in lib.build_reqs:
                spec.write('\n'.join([
                    "BuildRequires:  %s" % build_req ,
                    ""
                ]))
            spec.write('\n')

    spec.write('\n'.join([
        "Requires:       hicolor-icon-theme",
        ""]))
    spec.write('\n')

    for lib in nijiexpose_project_libs:
        if len(lib.requires) > 0:
            spec.write('\n'.join([
                "#%s deps" % lib.name ,
                ""
            ]))
            for req in lib.requires:
                spec.write('\n'.join([
                    "Requires:       %s" % req ,
                    ""
                ]))
            spec.write('\n')

    for lib in nijiexpose_indirect_libs:
        if len(lib.requires) > 0:
            spec.write('\n'.join([
                "#%s deps" % lib.name ,
                ""
            ]))
            for req in lib.requires:
                spec.write('\n'.join([
                    "Requires:       %s" % req ,
                    ""
                ]))
            spec.write('\n')
    spec.write('\n')

    spec.write('\n'.join([line[8:] for line in '''\
        %description
        nijilive is a framework for realtime 2D puppet animation which can be used for VTubing, 
        game development and digital animation. 
        nijiexpose is a tool that lets you use nijilive puppets as tracked avatars.
        This is an unbranded build, unsupported by the official project.


        '''.splitlines()]))

    # PREP
    spec.write('\n'.join([line[8:] for line in '''\
        %prep
        %setup -n %{name}-%{nijiexpose_commit}

        '''.splitlines()]))

    # GENERIC FIXES
    spec.write('\n'.join([line[8:] for line in '''\
        cat > source/nijiexpose/ver.d <<EOF
        module nijiexpose.ver;

        enum INS_VERSION = "%{nijiexpose_semver}";
        EOF

        # FIX: Add fake dependency
        mkdir -p deps/bindbc-spout2
        cat > deps/bindbc-spout2/dub.sdl <<EOF
        name "bindbc-spout2"
        EOF
        dub add-local deps/bindbc-spout2 "0.1.1"


        '''.splitlines()]))

    src_cnt = 2
    ptch_cnt = 0

    patch_list = []
    if Path("patches/%s" % "nijiexpose").exists():
        patch_list = list(Path("patches/%s" % "nijiexpose").glob("*.patch"))
        patch_list.sort()
    for file in patch_list:
        spec.write('\n'.join([
            "%%patch -P %d -p1 -b .%s-%s" % (
                ptch_cnt,
                *list(file.name[:-6].split("_")[0::2])),
            ""
        ]))
        ptch_cnt += 1

    # PREP DEPS
    spec.write('\n'.join([line[8:] for line in '''\
        mkdir -p deps

        # Project maintained deps
        '''.splitlines()]))

    for lib in nijiexpose_project_libs:
        spec.write('\n'.join([
            "tar -xzf %%{SOURCE%d}" % src_cnt,
            "mv %s deps/%s" % (
                lib.prep_file, lib.name), 
            "dub add-local deps/%s/ \"%%{%s_semver}\"" % (
                lib.name, lib.name.replace('-', '_').lower()),
            ""
        ]))
        src_cnt += 1

        spec.write('\n')
        spec.write('\n'.join([
            "pushd deps; pushd %s" % lib.name,
            ""
            ]))
        if len(lib.patches) > 0:
            spec.write('\n')
            for patch in lib.patches:
                spec.write('\n'.join([
                    "%%patch -P %d -p1 -b .%s-%s" % (
                        ptch_cnt,
                        *list(patch[:-6].split("_")[0::2])),
                    ""
                ]))
                ptch_cnt += 1

        if len(lib.file_sources) > 0:
            spec.write("\n")
            for i in range(len(lib.file_sources)):
                if lib.file_sources[i]["path"] != ".":
                    spec.write('\n'.join([
                        "mkdir -p ./%s" % lib.file_sources[i]["path"],
                        "cp --force %%{SOURCE%d} ./%s/" % (src_cnt, lib.file_sources[i]["path"]),
                        ""
                    ]))
                else:
                    spec.write('\n'.join([
                        "cp %%{SOURCE%d} ." % (src_cnt),
                        ""
                    ]))
                src_cnt += 1

        if len(lib.prep) > 0:
            prep = '\n'.join(lib.prep)
            c = 1
            while prep.find("%%{SOURCE%d}" % c) > 0:
                prep = prep.replace("%%{SOURCE%d}" % c, "%%{SOURCE%d}" % src_cnt)
                src_cnt += 1
                c += 1

            spec.write("\n")
            spec.write(prep)


        spec.write('\n'.join([
            "",
            "[ -f dub.sdl ] && dub convert -f json",
            "mv -f dub.json dub.json.base",
            "jq 'walk(if type == \"object\" then with_entries(select(.key | test(\"preBuildCommands*\") | not)) else . end)' dub.json.base > dub.json",
            ""
        ]))

        spec.write('\n'.join([
            "",
            "popd; popd",
            ""
            ]))

        spec.write('\n')

    spec.write('\n')

    # BUILD
    spec.write('\n'.join([line[8:] for line in '''\
        %build
        export DFLAGS="%{_d_optflags} -L-rpath=%{_libdir}/nijiexpose/"
        dub build \\
            --cache=local \\
            --config=linux-full \\
            --skip-registry=all \\
            --non-interactive \\
            --temp-build \\
            --compiler=ldc2
        mkdir ./out/
        cp /tmp/.dub/build/nijiexpose*/linux-full*/* ./out/


        '''.splitlines()]))

    # INSTALL

    spec.write('\n'.join([line[8:] for line in '''\
        %install
        install -d ${RPM_BUILD_ROOT}%{_libdir}/nijiexpose
        install -p ./out/cimgui.so ${RPM_BUILD_ROOT}%{_libdir}/nijiexpose/cimgui.so

        install -d ${RPM_BUILD_ROOT}%{_bindir}
        install -p ./out/nijiexpose ${RPM_BUILD_ROOT}%{_bindir}/nijiexpose

        install -d ${RPM_BUILD_ROOT}%{_datadir}/applications/
        install -p -m 644 ./build-aux/linux/nijiexpose.desktop ${RPM_BUILD_ROOT}%{_datadir}/applications/nijiexpose.desktop
        desktop-file-validate \\
            ${RPM_BUILD_ROOT}%{_datadir}/applications/nijiexpose.desktop

        install -d ${RPM_BUILD_ROOT}%{_metainfodir}/
        install -p -m 644 ./build-aux/linux/nijiexpose.appdata.xml ${RPM_BUILD_ROOT}%{_metainfodir}/nijiexpose.appdata.xml
        appstream-util validate-relax --nonet \\
            ${RPM_BUILD_ROOT}%{_metainfodir}/nijiexpose.appdata.xml

        install -d $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/256x256/apps/
        install -p -m 644 %{SOURCE1} $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/256x256/apps/nijiexpose.png

        '''.splitlines()]))
    
    # INSTALL LICENSES
    spec.write('\n'.join([line[8:] for line in '''\
        # Dependency licenses
        install -d ${RPM_BUILD_ROOT}%{_datadir}/licenses/%{name}/deps/
        find ./deps/ -mindepth 1 -maxdepth 1 -exec \\
            install -d ${RPM_BUILD_ROOT}%{_datadir}/licenses/%{name}/{} ';'

        find ./deps/ -mindepth 2 -maxdepth 2 -iname '*LICENSE*' -exec \\
            install -p -m 644 "{}" "${RPM_BUILD_ROOT}%{_datadir}/licenses/%{name}/{}" ';'

        install -d ${RPM_BUILD_ROOT}%{_datadir}/licenses/%{name}/res/
        find ./res/ -mindepth 1 -maxdepth 1 -iname '*LICENSE*' -exec \\
            install -p -m 644 {} ${RPM_BUILD_ROOT}%{_datadir}/licenses/%{name}/{} ';'


        '''.splitlines()]))

    # FILES
    spec.write('\n'.join([line[8:] for line in '''\
        %files
        %license LICENSE
        %{_datadir}/licenses/%{name}/*
        %{_bindir}/nijiexpose
        %{_libdir}/nijiexpose/*
        %{_metainfodir}/nijiexpose.appdata.xml
        %{_datadir}/applications/nijiexpose.desktop
        %{_datadir}/icons/hicolor/256x256/apps/nijiexpose.png


        %changelog
        %autochangelog
        '''.splitlines()][:-1]))
