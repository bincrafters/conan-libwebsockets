from os import path
import tempfile
from conans import ConanFile, CMake, tools


class LibwebsocketsConan(ConanFile):
    name = "libwesockets"
    version = "2.4.0"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    options = {"shared": [True, False], "lws_with_ssl": [True, False]}
    default_options = "shared=True", "lws_with_ssl=True"
    url = "https://github.com/bincrafters/conan-libwebsockets"
    description = "Canonical libwebsockets.org websocket library"
    license = "https://github.com/warmcat/libwebsockets/blob/master/LICENSE"
    exports_sources = "CMakeLists.txt"
    exports = "LICENSE"
    root = name + "-" + version
    install_dir = tempfile.mkdtemp(prefix=root)

    def configure(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.lws_with_ssl:
            self.requires.add("OpenSSL/1.0.2l@conan/stable")

    def source(self):
        source_url = "https://github.com/warmcat/libwebsockets"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))

    def build(self):
        cmake = CMake(self)
        cmake.definitions["LWS_WITHOUT_TESTAPPS"] = True
        cmake.definitions["LWS_WITH_SHARED"] = self.options.shared
        cmake.definitions["LWS_WITH_STATIC"] = not self.options.shared
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.install_dir
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="LICENSE", dst=".", src=path.join(self.root, "LICENSE"))
        self.copy(pattern="*.h", dst="include", src=path.join(self.install_dir, "include"))
        self.copy(pattern="*.cmake", dst="res", src=path.join(self.install_dir, "lib"))
        self.copy(pattern="*.pc", dst="res", src=path.join(self.install_dir, "lib"))
        self.copy(pattern="*.so*", dst="lib", src=path.join(self.install_dir, "lib"), keep_path=False)
        self.copy(pattern="*.a", dst="lib", src=path.join(self.install_dir, "lib"), keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=path.join(self.install_dir, "lib"), keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs =  tools.collect_libs(self)
