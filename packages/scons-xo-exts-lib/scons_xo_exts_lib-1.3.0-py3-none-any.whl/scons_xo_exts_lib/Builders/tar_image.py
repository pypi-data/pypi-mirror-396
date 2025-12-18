#!/usr/bin/env python


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import subprocess

from SCons.Script import Builder

from scons_xo_exts_lib.BuildSupport import NodeMangling


def tar_image_action(target, source, env):
    target_tar = NodeMangling.get_first_node(target)
    directory = NodeMangling.get_first_directory(source)

    cmd = f"tar --auto-compress --create --file {target_tar.abspath} ."

    result = subprocess.run(
        args=cmd,
        capture_output=False,
        check=False,
        shell=True,
        cwd=directory,
    )

    return result.returncode


def generate(env) -> None:
    tar_image_builder = Builder(action=tar_image_action)

    env.Append(BUILDERS={"TarImage": tar_image_builder})


def exists(env):
    return env.Detect("tar_image")
