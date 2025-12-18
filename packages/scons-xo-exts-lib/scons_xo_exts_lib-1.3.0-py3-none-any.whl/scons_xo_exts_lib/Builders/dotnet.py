#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import platform
import subprocess

from typing import List

from SCons.Script import Builder
from SCons.Script import Environment

from scons_xo_exts_lib.BuildSupport import NodeMangling


def _dotnet_get_dotnet_exe(env: Environment) -> str:
    dotnet_exe = env.get("DOTNET_EXE")

    if dotnet_exe:
        return dotnet_exe

    try:
        return os.path.join(env["DOTNET_ROOT"], "dotnet")
    except KeyError:
        return "dotnet"


def _dotnet_get_project(source) -> str:
    regex = ".*\\.(cs|fs|vb|)proj$"

    try:
        node = NodeMangling.regex_find_node(regex=regex, nodes=source)

        return str(node.abspath)
    except Exception as exception:
        raise RuntimeError("No dotnet project file found", exception)


def _dotnet_command(env: Environment, source, args: List[str]) -> None:
    project_file = _dotnet_get_project(source=source)
    source_directory = os.path.dirname(project_file)

    extra_variables = {
        "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
        "DOTNET_NOLOGO": "1",
        "DOTNET_SKIP_FIRST_TIME_EXPERIENCE": "1",
        "MSBUILDTERMINALLOGGER": "off",
    }

    subprocess_env = env.Clone()["ENV"]
    subprocess_env.update(extra_variables)

    dotnet_exe = _dotnet_get_dotnet_exe(env=env)

    cmd = [dotnet_exe] + args
    print(cmd)

    result = subprocess.run(
        args=cmd,
        capture_output=False,
        check=False,
        cwd=source_directory,
        env=subprocess_env,
    )

    if result.returncode == 0:
        return

    raise RuntimeError("Dotnet command failed")


def _dotnet_detect_rid() -> str:
    """
    Returns a dotnet runtime identifier string in the format "{os}-{arch}".

    OS values: linux, linux-musl, windows, osx
    Arch values: x64, x86, arm, arm64
    """

    os_name = "unknownos"
    os_arch = "unknownarch"

    py_os_name = platform.system().lower()
    py_os_arch = platform.machine().lower()

    match py_os_name:
        case "linux":
            if platform.libc_ver()[0] == "glibc":
                os_name = "linux"
            else:
                os_name = "linux-musl"
        case "darwin":
            os_name = "osx"
        case "windows":
            os_name = "win"
        case _:
            os_name = py_os_name

    match py_os_arch:
        case "x86_64" | "amd64":
            os_arch = "x64"
        case "i386" | "i686":
            os_arch = "x86"
        case "aarch64":
            os_arch = "arm64"
        case _:
            os_arch = py_os_arch

    return f"{os_name}-{os_arch}"


def _dotnet_get_rid(env: Environment) -> str:
    key = "DOTNET_RUNTIME"

    if key in env:
        return env[key]

    return _dotnet_detect_rid()


def _dotnet_get_configuration(env: Environment) -> str:
    key = "DOTNET_CONFIGURATION"

    if key in env:
        return env[key]

    return "Release"


def _dotnet_restore(env: Environment, source) -> None:
    runtime = _dotnet_get_rid(env=env)

    _dotnet_command(
        env=env,
        source=source,
        args=[
            "restore",
            "--force-evaluate",
            f"--runtime={runtime}",
        ],
    )


def _dotnet_build(env: Environment, source) -> None:
    runtime = _dotnet_get_rid(env=env)
    configuration = _dotnet_get_configuration(env=env)

    _dotnet_command(
        env=env,
        source=source,
        args=[
            "build",
            "--no-restore",
            f"--runtime={runtime}",
            f"--configuration={configuration}",
        ],
    )


def _dotnet_compile(*args, **kwargs) -> None:
    _dotnet_restore(*args, **kwargs)
    _dotnet_build(*args, **kwargs)


def _dotnet_pack(env: Environment, source, target) -> None:
    runtime = _dotnet_get_rid(env=env)
    configuration = _dotnet_get_configuration(env=env)

    target_directory = NodeMangling.get_first_directory(nodes=target)

    _dotnet_command(
        env=env,
        source=source,
        args=[
            "pack",
            "--no-restore",
            f"--runtime={runtime}",
            f"--configuration={configuration}",
            f"--output={target_directory}",
        ],
    )


def _dotnet_compile_binary(env: Environment, source, target) -> None:
    runtime = _dotnet_get_rid(env=env)
    configuration = _dotnet_get_configuration(env=env)

    target_directory = NodeMangling.get_first_directory(nodes=target)

    _dotnet_command(
        env=env,
        source=source,
        args=[
            "publish",
            "--no-restore",
            "--self-contained",
            "-p:PublishSingleFile=true",
            f"--runtime={runtime}",
            f"--configuration={configuration}",
            f"--output={target_directory}",
        ],
    )


def dotnet_package_build_action(target, source, env: Environment) -> int:
    try:
        _dotnet_compile(env=env, source=source)
        _dotnet_pack(env=env, source=source, target=target)
    except RuntimeError:
        return 1

    return 0


def dotnet_binary_build_action(target, source, env) -> int:
    try:
        _dotnet_compile(env=env, source=source)
        _dotnet_compile_binary(env=env, source=source, target=target)
    except RuntimeError:
        return 1

    return 0


def generate(env: Environment) -> None:
    dotnet_binary_builder = Builder(action=dotnet_binary_build_action)
    dotnet_package_builder = Builder(action=dotnet_package_build_action)

    env.Append(
        BUILDERS={
            "DotnetBinary": dotnet_binary_builder,
            "DotnetPackage": dotnet_package_builder,
        }
    )


def exists(env: Environment):
    return env.Detect("dotnet")
