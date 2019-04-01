# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.util.env_reader import get_env

import os
import shutil
import tempfile


class LibnslConan(ConanFile):
    name = "libnsl"
    version = "1.2.0"
    description = "libnsl contains the public client interface for NIS(YP) and NIS+ in a IPv6 ready version"
    topics = ("conan", "libnsl", "RPC")
    url = "https://github.com/bincrafters/conan-libnsl"
    homepage = "https://github.com/thkukuk/libnsl/"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "LGPL-2.1"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = (
        "LICENSE.md",
    )
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    _source_subfolder = "sources"
    generators = "pkg_config",

    def config_options(self):
        del self.settings.compiler.libcxx
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libtirpc/1.1.4@bincrafters/stable")

    def source(self):
        name = "libnsl"
        filename = "{}-{}.tar.gz".format(self.name, self.version)
        url = "https://github.com/thkukuk/{}/archive/v{}.tar.gz".format(name, self.version)
        sha256 = "a5a28ef17c4ca23a005a729257c959620b09f8c7f99d0edbfe2eb6b06bafd3f8"

        dlfilepath = os.path.join(tempfile.gettempdir(), filename)
        if os.path.exists(dlfilepath) and not get_env("LIBNSL2_FORCE_DOWNLOAD", False):
            self.output.info("Skipping download. Using cached {}".format(dlfilepath))
        else:
            self.output.info("Downloading {} from {}".format(self.name, url))
            tools.download(url, dlfilepath)
        tools.check_sha256(dlfilepath, sha256)
        tools.untargz(dlfilepath)
        extracted_dir = "{}-{}".format(name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "po", "Makefile.in.in"),
                              "GETTEXT_MACRO_VERSION = 0.19",
                              "GETTEXT_MACRO_VERSION = @GETTEXT_MACRO_VERSION@")

        with tools.chdir(os.path.join(self.source_folder, self._source_subfolder)):
            self.run("./autogen.sh", win_bash=tools.os_info.is_windows)  # needs gettext-devel on fedora linux

    def build(self):
        conf_args = [
            "--disable-static" if self.options.shared else "--enable-static",
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--disable-static" if self.options.shared else "--enable-static",
        ]
        if not self.options.shared:
            conf_args.append("--with-pic" if self.options.fPIC else "--without-pic")
        if self.should_build:
            autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            if self.settings.compiler in ("gcc", "clang", ):
                autotools.libs.append("pthread")
            autotools.configure(configure_dir=os.path.join(self.source_folder, self._source_subfolder), args=conf_args)
            autotools.make()

    def package(self):
        if self.should_install:
            with tools.chdir(self.build_folder):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.install()
        shutil.rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"))
        libtool_path = os.path.join(self.package_folder, "lib", "libnsl.la")
        if os.path.exists(libtool_path):
            os.remove(libtool_path)

        self.copy("LICENSE.md", src=self.source_folder, dst="licenses")
        self.copy("COPYING", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")

    def package_info(self):
        self.cpp_info.includedirs = ["include", "include/libnsl"]
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.compiler in ("gcc", "clang", ):
            self.cpp_info.libs.append("pthread")
