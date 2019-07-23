# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration

import os


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
    _source_subfolder = "source_subfolder"
    generators = "pkg_config",

    def config_options(self):
        if self.options.shared:
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("libnsl is only supported by Linux.")

    def requirements(self):
        self.requires("libtirpc/1.1.4@bincrafters/stable")

    def source(self):
        sha256 = "a5a28ef17c4ca23a005a729257c959620b09f8c7f99d0edbfe2eb6b06bafd3f8"

        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        extracted_dir = self.name + "-" + self.version

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
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        libtool_path = os.path.join(self.package_folder, "lib", "libnsl.la")
        if os.path.exists(libtool_path):
            os.remove(libtool_path)

        self.copy("COPYING", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")

    def package_info(self):
        self.cpp_info.includedirs = ["include", os.path.join("include", "rpcsvc")]
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.compiler in ("gcc", "clang", ):
            self.cpp_info.libs.append("pthread")
