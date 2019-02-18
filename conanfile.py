# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
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
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    _source_subfolder = "sources"
    requires = ("libtirpc/1.1.4@bincrafters/stable", )

    def config_options(self):
        del self.settings.compiler.libcxx
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        url = "https://github.com/thkukuk/{name}/archive/v{version}.tar.gz".format(
            name=self.name, version=self.version
        )
        sha256 = "a5a28ef17c4ca23a005a729257c959620b09f8c7f99d0edbfe2eb6b06bafd3f8"
        tools.get(url, sha256=sha256)
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)
        with tools.chdir(os.path.join(self.source_folder, self._source_subfolder)):
            self.run("./autogen.sh")  # needs gettext-devel on fedora linux

    def build(self):
        conf_args = [
            "--disable-static" if self.options.shared else "--enable-static",
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--disable-static" if self.options.shared else "--enable-static",
        ]
        if not self.options.shared:
            conf_args.append("--with-pic" if self.options.fPIC else "--without-pic")
        if self.should_build:
            autotools = AutoToolsBuildEnvironment(self)
            if self.compiler in ("gcc", "clang", ):
                autotools.libs.append("pthread")
            autotools.configure(configure_dir=os.path.join(self.source_folder, self._source_subfolder), args=conf_args)
            autotools.make()

    def package(self):
        if self.should_install:
            with tools.chdir(self.build_folder):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.install()

    def package_info(self):
        self.cpp_info.includedirs = ["include", "include/libnsl"]
        self.cpp_info.libs = tools.collect_libs(self)
        if self.compiler in ("gcc", "clang", ):
            self.cpp_info.libs.append("pthread")
