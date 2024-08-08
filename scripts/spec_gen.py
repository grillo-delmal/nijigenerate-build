import math
import json
from pathlib import Path

class LibData:
    def __init__(self, name, deps, gitver, semver = None, dist = 0, commit = "0000000", extra_consts={}):

        # Try load specfile data
        try:
            spec_data = {}
            with open("spec_data/%s.json" % name) as f:
                spec_data = json.load(f)
        except FileNotFoundError:
            pass

        if Path("files/%s" % name).exists():
            spec_data = spec_data | {
                "file_sources": [
                    {
                        "name": file.name, 
                        "path": str(file.relative_to("files/%s" % name).parent)} 
                    for file in Path("files/%s" % name).glob("**/*") 
                    if file.is_file()]}

        if Path("patches/%s" % name).exists():
            spec_data = spec_data | {
                "patches": [
                    file.name 
                    for file in Path("patches/%s" % name).glob("*.patch")]}

        self.name = name
        self.gitver = gitver
        if semver is None:
            self.semver = self.gitver
        else:
            self.semver = semver
        self.extra_consts = extra_consts
        self.dist = dist
        self.commit = commit
        self.deps = deps
        self.deps.sort()

        self.summary = spec_data["summary"] \
            if "summary" in spec_data \
            else "%{lib_name} library for D"
            
        self.licenses = sorted(set(spec_data["licenses"] \
            if "licenses" in spec_data \
            else ["BSD-2-Clause"]))

        self.url = spec_data["url"] \
            if "url" in spec_data \
            else "https://github.com/Inochi2D/%{lib_name}"

        self.description = spec_data["description"] \
            if "description" in spec_data \
            else [
                "An actual description of %{lib_name}",
                "#FIXME: generate an actual description",
                ""]

        self.prep_file = spec_data["prep_file"] \
            if "prep_file" in spec_data \
            else "%s-%%{%s_commit}" % (
                self.name, self.name.replace('-', '_').lower()) \
                if semver is not None \
                else "%{lib_name}-%{lib_gitver}"

        self.macros = spec_data["macros"] \
            if "macros" in spec_data \
            else []

        self.vars = spec_data["vars"] \
            if "vars" in spec_data \
            else {}

        self.source = spec_data["source"] \
            if "source" in spec_data \
            else \
                "https://github.com/Inochi2D/%s" \
                "/archive/refs/tags/v%%{lib_gitver}" \
                "/%s-%%{lib_gitver}.tar.gz" % (
                    self.name,
                    self.name
                )
        self.ex_sources = spec_data["ex_sources"] \
            if "ex_sources" in spec_data \
            else []

        self.files = spec_data["files"] \
            if "files" in spec_data \
            else []

        self.patches = spec_data["patches"] \
            if "patches" in spec_data \
            else []

        self.file_sources = spec_data["file_sources"] \
            if "file_sources" in spec_data \
            else []

        self.build_reqs = spec_data["build_reqs"] \
            if "build_reqs" in spec_data \
            else []

        self.requires = spec_data["requires"] \
            if "requires" in spec_data \
            else []

        self.prep = spec_data["prep"] \
            if "prep" in spec_data \
            else []

        self.build = spec_data["build"] \
            if "build" in spec_data \
            else []

        self.check = spec_data["check"] \
            if "check" in spec_data \
            else []

        self.install = spec_data["install"] \
            if "install" in spec_data \
            else []


class LibSpecFile(LibData):

    def spec_gen(self, path):

        with open(path, 'w') as f:

            # Macros

            f.write('\n'.join([
                "%global debug_package %{nil}",
                ""
            ]))
            if len(self.macros) > 0:
                f.write('\n'.join(self.macros))

            # Variables

            f.write('\n'.join([
                "",
                "%%define lib_name      %s" % self.name,
                "%%define lib_ver       %s" % self.gitver.split("-")[0],
                "%%define lib_gitver    %s" % self.gitver,
                "%%define lib_semver    %s" % self.semver,
                "%%define lib_dist      %s" % self.dist,
                "%%define lib_commit    %s" % self.commit,
                "%%define lib_short     %s" % self.commit[:7],
                ""
            ]))
            for key in self.vars.keys():
                f.write('\n'.join([
                    "%%define %s%s %s" % (
                        key,
                        " " * (13-len(key)),
                        self.vars[key]) ,
                    ""
                ]))
            for key in self.extra_consts.keys():
                f.write('\n'.join([
                    "%%define %s%s %s" % (
                        key,
                        " " * (13-len(key)),
                        self.extra_consts[key]) ,
                    ""
                ]))
            f.write('\n'.join([
                "",
                "%if 0%{lib_dist} > 0",
                "%define lib_suffix ^%{lib_dist}.git%{lib_short}",
                "%endif",
                "",
                ""
            ]))

            # General description

            f.write('\n'.join([
                "Name:           zdub-%{lib_name}",
                "Version:        %{lib_ver}%{?lib_suffix:}",
                "Release:        %autorelease",
                "Summary:        %s" % (self.summary),
                "Group:          Development/Libraries",
                "License:        %s" % (" and ".join(self.licenses)),
                "URL:            %s" % (self.url),
                ""
            ]))

            # Sources and patches

            f.write('\n'.join([
                "Source0:        %s" % self.source,
                ""
            ]))

            src_cnt = 1
            for src in self.ex_sources:
                f.write('\n'.join([
                    "Source%d:%s%s" % (
                        src_cnt, 
                        " " * (8 - math.floor(math.log10(src_cnt))), 
                        src) ,
                    ""
                ]))
                src_cnt += 1

            if len(self.file_sources) > 0:
                for src in self.file_sources:
                    f.write('\n'.join([
                        "Source%d:%s%s" % (
                            src_cnt, 
                            " " * (8 - math.floor(math.log10(src_cnt))), 
                            src["name"]) ,
                        ""
                    ]))

            if len(self.patches) > 0:
                f.write("\n")
                for i in range(len(self.patches)):
                    f.write('\n'.join([
                        "Patch%d:%s%s" % (
                            i, 
                            " " * (9 - math.floor(math.log10(i) if i > 0 else 0)), 
                            self.patches[i]) ,
                        ""
                    ]))
            f.write('\n')

            # Build Requirements

            f.write('\n'.join([
                "BuildRequires:  setgittag",
                "BuildRequires:  git",
                "BuildRequires:  ldc",
                "BuildRequires:  dub",
                ""
            ]))
            for dep in self.deps:
                f.write("BuildRequires:  zdub-%s-static\n" % dep)

            for build_req in self.build_reqs:
                f.write('\n'.join([
                    "BuildRequires:  %s" % build_req ,
                    ""
                ]))
            f.write('\n')
            f.write('\n')

            # Description

            f.write('\n'.join([
                "%description",
                ""
            ]))
            f.write('\n'.join(self.description))
            f.write('\n')
            f.write('\n')

            # Devel package info and requirements

            f.write('\n'.join([
                "%package devel",
                "Provides:       %{name}-static = %{version}-%{release}",
                "Summary:        Support to use %{lib_name} for developing D applications",
                "Group:          Development/Libraries",
                "",
                "Requires:       zdub-dub-settings-hack",
                ""
            ]))
            for dep in self.deps:
                f.write("Requires:       zdub-%s-static\n" % dep)

            if len(self.requires) > 0:
                f.write('\n')
                for req in self.requires:
                    f.write("Requires:       %s\n" % req)
            f.write('\n'.join([
                "",
                "",
                "%description devel",
                "Sources to use the %{lib_name} library on dub using the",
                "zdub-dub-settings-hack method.",
                ""
            ]))
            f.write('\n')
            f.write('\n')

            # Preparation

            f.write('\n'.join([
                "%prep",
                ""
            ]))
            f.write('\n'.join([
                "%%autosetup -n %s -p1" % self.prep_file,
                ""
            ]))
            f.write('\n'.join([
                "setgittag --rm -f v%{lib_gitver}",
                ""
            ]))
            if len(self.file_sources) > 0:
                f.write("\n")
                src_cnt = 1
                for i in range(len(self.file_sources)):
                    if self.file_sources[i]["path"] != ".":
                        f.write('\n'.join([
                            "mkdir -p ./%s" % self.file_sources[i]["path"],
                            "cp --force %%{SOURCE%d} ./%s/" % (i + src_cnt, self.file_sources[i]["path"]),
                            ""
                        ]))
                    else:
                        f.write('\n'.join([
                            "cp %%{SOURCE%d} ." % (i + src_cnt),
                            ""
                        ]))
            if len(self.prep) > 0:
                f.write("\n")
                f.write('\n'.join(self.prep))
            f.write('\n')
            f.write('\n')

            # Build data
            if len(self.build) > 0:
                f.write('\n'.join([
                    "%build",
                    ""
                ]))
                f.write('\n'.join(self.build))
                f.write('\n')
                f.write('\n')

            # Check
            f.write('\n'.join([
                "%check",
                ""
            ]))

            if len(self.check) > 0:
                f.write('\n'.join(self.check))
            else:
                f.write('\n'.join([
                    "dub build \\",
                    "    --cache=local --temp-build \\",
                    "    --skip-registry=all \\",
                    "    --compiler=ldc2 \\",
                    "    --deep",
                    "dub clean",
                    ""
                ]))

            f.write('\n')
            f.write('\n')

            # Install data

            f.write('\n'.join([
                "%install",
                "mkdir -p %{buildroot}%{_includedir}/zdub/%{lib_name}/%{lib_gitver}",
                "cp -r "
                    ". "
                    "%{buildroot}%{_includedir}/zdub/%{lib_name}/%{lib_gitver}/%{lib_name}",
                ""
            ]))
            if len(self.install) > 0:
                f.write('\n'.join(self.install))
            f.write('\n')
            f.write('\n')

            # File list

            f.write('\n'.join([
                "%files devel",
                "%license LICENSE",
                "%{_includedir}/zdub/%{lib_name}/%{lib_gitver}/%{lib_name}/",
                ""
            ]))
            if len(self.files) > 0:
                f.write('\n'.join(self.files))
            f.write('\n'.join([
                "",
                "",
                "%changelog",
                "%autochangelog",
                ""
            ]))
