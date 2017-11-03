
from os import path
import tempfile
from conans import ConanFile, CMake, tools


class LibwebsocketsConan(ConanFile):
    name = "libwebsockets"
    version = "2.4.0"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    options = {"shared": [True, False], "lws_with_libuv": [True, False], "lws_with_libevent": [True, False]}
    default_options = "shared=True", "lws_with_libuv=False", "lws_with_libevent=False"
    url = "https://github.com/bincrafters/conan-libwebsockets"
    description = "Canonical libwebsockets.org websocket library"
    license = "https://github.com/warmcat/libwebsockets/blob/master/LICENSE"
    exports_sources = "CMakeLists.txt"
    exports = "LICENSE"
    root = name + "-" + version
    install_dir = tempfile.mkdtemp(prefix=root)
    requires = "OpenSSL/1.0.2l@conan/stable"

    def configure(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.lws_with_libuv:
            self.requires.add("libuv/1.15.0@%s/stable" % self.user)
            self.options["libuv"].shared = self.options.shared
        if self.options.lws_with_libevent:
            self.requires.add("libevent/2.1.8@%s/stable" % self.user)
            self.options["libevent"].shared = self.options.shared

    def source(self):
        source_url = "https://github.com/warmcat/libwebsockets"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))

    def build(self):
        self._use_conan_zlib()
        cmake = CMake(self)
        cmake.definitions["LWS_WITHOUT_TESTAPPS"] = True
        cmake.definitions["LWS_LINK_TESTAPPS_DYNAMIC"] = True
        cmake.definitions["LWS_WITH_SHARED"] = self.options.shared
        cmake.definitions["LWS_WITH_STATIC"] = not self.options.shared
        cmake.definitions["LWS_WITH_SSL"] = True
        cmake.definitions["LWS_WITH_ZLIB"] = True
        cmake.definitions["LWS_WITH_LIBUV"] = self.options.lws_with_libuv
        cmake.definitions["LWS_WITH_LIBEVENT"] = self.options.lws_with_libevent
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.install_dir
        cmake.configure()
        cmake.build()
        cmake.install()

    def _use_conan_zlib(self):
        if self.settings.os == "Windows":
            with tools.chdir(self.root):
                tools.replace_in_file("CMakeLists.txt", "set(LWS_WITH_BUNDLED_ZLIB_DEFAULT ON)", "")

    def package(self):
        self.copy(pattern="LICENSE", dst=".", src=path.join(self.root, "LICENSE"))
        self.copy(pattern="*.h", dst="include", src=path.join(self.install_dir, "include"))
        cmake_dir = "cmake" if self.settings.os == "Windows" else "lib"
        self.copy(pattern="*.cmake", dst="res", src=path.join(self.install_dir, cmake_dir))
        if self.settings.os == "Windows":
            self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
        else:
            self.copy(pattern="*.pc", dst="res", src=path.join(self.install_dir, "lib"))
            if self.options.shared:
                if self.settings.os == "Linux":
                    self.copy(pattern="*.so*", dst="lib", src=path.join(self.install_dir, "lib"), keep_path=False)
                elif self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", src=path.join(self.install_dir, "lib"), keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", src=path.join(self.install_dir, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs =  tools.collect_libs(self)
