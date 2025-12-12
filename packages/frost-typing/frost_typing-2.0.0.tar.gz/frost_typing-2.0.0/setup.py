# -*- coding: utf-8 -*-
import os
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class FrostBuildExt(build_ext):

    def build_extensions(self) -> None:
        compiler = self.compiler.compiler_type

        extra_compile_args: list[str] = []
        extra_link_args: list[str] = []
        if compiler in {"unix", "mingw32", "gcc", "clang"}:
            extra_link_args = [
                "-s",
                "-Wl,--gc-sections",
                "-Wl,--strip-all",
                "-fno-semantic-interposition",
            ]

            extra_compile_args = [
                "-O3",
                "-std=gnu11",
                "-fomit-frame-pointer",
                "-DNDEBUG",
                "-fno-ident",
                "-fno-exceptions",
                "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables",
                "-fvisibility=hidden",
                "-fno-stack-protector",
                "-ffunction-sections",
                "-fdata-sections",

                # Diagnostics
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                "-Werror",
                "-Wunused-const-variable",
                "-Wunused-function",
                "-Wunused-macros",
            ]

        elif compiler == "msvc":
            extra_link_args = ["/LTCG", "/OPT:REF", "/OPT:ICF", "/INCREMENTAL:NO"]
            extra_compile_args = ["/O2", "/Oy", "/GL", "/GS-", "/std:c11", "/DNDEBUG", "/W3", "/Zc:inline"]

        for ext in self.extensions:
            ext.extra_link_args = extra_link_args
            ext.extra_compile_args = extra_compile_args

        build_ext.build_extensions(self)


def find_sources(directory: str, suffix: str) -> list[str]:
    sources: list[str] = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(suffix):
                sources.append(os.path.join(root, file))
    return sources


if __name__ == "__main__":
    setup(
        cmdclass={"build_ext": FrostBuildExt},
        ext_modules=[
            Extension(
                # define_macros=[("USED_JSON_SCHEMA", "1")],  # Find it in beta testing
                sources=find_sources("src", ".c"),
                name="frost_typing.frost_typing",
                include_dirs=["include"],
            )
        ],
    )
