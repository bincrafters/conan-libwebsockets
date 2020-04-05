import os
from conans import ConanFile, CMake, tools


class LibwebsocketsConan(ConanFile):
    name = "libwebsockets"
    version = "3.2.2"
    description = "Canonical libwebsockets.org websocket library"
    url = "https://github.com/bincrafters/conan-libwebsockets"
    homepage = "https://github.com/warmcat/libwebsockets"
    license = "LGPL-2.1"
    topics = ("conan", "libwebsockets", "websocket")
    exports = "LICENSE.md"
    exports_sources = "CMakeLists.txt"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "lws_with_libuv": [True, False],
        "lws_with_libevent": [True, False],
        "lws_with_zlib": [True, False],
        "lws_with_ssl": [True, False]
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'lws_with_libuv': False,
        'lws_with_libevent': False,
        'lws_with_zlib': False,
        'lws_with_ssl': False
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.lws_with_libuv:
            self.requires.add("libuv/1.34.2")
        if self.options.lws_with_libevent:
            self.requires.add("libevent/2.1.11")
        if self.options.lws_with_zlib:
            self.requires.add("zlib/1.2.11")
        if self.options.lws_with_ssl:
            self.requires.add("openssl/1.0.2u")

    def source(self):
        sha256 = "166d6e17cab64bfc10c2a71799c298284540a1fa63f6ea3de5caccb34502243c"
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
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

        if not self.options.shared and self.settings.os != "Windows":
            cmake.definitions["LWS_STATIC_PIC"] = self.options.fPIC

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "m"])
