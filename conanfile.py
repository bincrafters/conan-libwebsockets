#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools


class LibwebsocketsConan(ConanFile):
    name = "libwebsockets"
    version = "2.4.0"
    description = "Canonical libwebsockets.org websocket library"
    url = "https://github.com/bincrafters/conan-libwebsockets"
    license = "LGPL-2.1"
    exports = "LICENSE.md"
    exports_sources = "CMakeLists.txt"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    options = {
        "shared": [True, False], 
        "lws_with_libuv": [True, False], 
        "lws_with_libevent": [True, False],
        "lws_with_zlib": [True, False],
        "lws_with_ssl": [True, False]
    }
    default_options = {'shared': True, 'lws_with_libuv': False, 'lws_with_libevent': False, 'lws_with_zlib': False, 'lws_with_ssl': False}
        
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.lws_with_libuv:
            self.requires.add("libuv/[>=1.15.0]@bincrafters/stable")
        if self.options.lws_with_libevent:
            self.requires.add("libevent/[>=2.1.8]@bincrafters/stable")
        if self.options.lws_with_zlib:
            self.requires.add("zlib/[>=1.2.8]@conan/stable")
        if self.options.lws_with_ssl:
            self.requires.add("OpenSSL/[>=1.0.2l]@conan/stable")
            
    def source(self):
        source_url = "https://github.com/warmcat/libwebsockets"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["LWS_WITHOUT_TESTAPPS"] = True
        cmake.definitions["LWS_LINK_TESTAPPS_DYNAMIC"] = True
        cmake.definitions["LWS_WITH_SHARED"] = self.options.shared
        cmake.definitions["LWS_WITH_STATIC"] = not self.options.shared
        cmake.definitions["LWS_WITH_SSL"] = self.options.lws_with_ssl
        cmake.definitions["LWS_WITH_LIBUV"] = self.options.lws_with_libuv
        cmake.definitions["LWS_WITH_LIBEVENT"] = self.options.lws_with_libevent
        cmake.definitions["LWS_WITH_ZLIB"] = self.options.lws_with_zlib
        if not self.options.lws_with_zlib:
            cmake.definitions["LWS_WITHOUT_EXTENSIONS"] = True 
            cmake.definitions["LWS_WITH_ZIP_FOPS"] = False 
        # zlib is required for extensions

        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.package_folder
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="license", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs =  tools.collect_libs(self)
