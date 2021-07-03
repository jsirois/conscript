from __future__ import absolute_import

import hashlib
import json
import os
import subprocess
import sys
from textwrap import dedent

import pytest  # type: ignore

TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Callable, Iterable

    CreateConscript = Callable[[Iterable[str]], str]
    CreateProject = Callable[[str, str], str]


@pytest.fixture(scope="session")
def project_root_dir():
    # type: () -> str
    return os.path.dirname(os.path.dirname(__file__))


@pytest.fixture(scope="session")
def create_conscript(
    tmpdir_factory,  # type: Any
    project_root_dir,  # type: str
):
    # type: (...) -> CreateConscript

    def create_conscript_pex(requirements):
        # type: (Iterable[str]) -> str
        pex = os.path.join(
            str(
                tmpdir_factory.mktemp(
                    hashlib.sha1(json.dumps(sorted(list(requirements))).encode("utf8")).hexdigest()
                )
            ),
            "conscript.pex",
        )
        args = [sys.executable, "-m", "pex", project_root_dir]
        args.extend(requirements)
        args.extend(["-c", "conscript", "-o", pex])
        subprocess.check_call(args)
        return pex

    return create_conscript_pex


@pytest.fixture(scope="session")
def create_project(tmpdir_factory):
    # type: (Any) -> CreateProject

    def create_project(
        name,  # type: str
        version,  # type: str
    ):
        # type: (...) -> str
        project_directory = tmpdir_factory.mktemp(name)

        with open(os.path.join(str(project_directory), "{}.py".format(name)), "w") as fp:
            fp.write(
                dedent(
                    """\
                    import argparse
                    import sys


                    __version__ = {version!r}


                    def main():
                        parser = argparse.ArgumentParser(description="The {name} program.")
                        parser.add_argument(
                            "-V", "--version", action="version", version={version!r}
                        )
                        parser.parse_args()
                        parser.print_help()
                        sys.exit(0)
                    """
                ).format(name=name, version=version)
            )

        with open(os.path.join(str(project_directory), "setup.cfg"), "w") as fp:
            fp.write(
                dedent(
                    """\
                    [metadata]
                    name = {name}
                    version = {version}

                    [options]
                    py_modules = {name}

                    [options.entry_points]
                    console_scripts =
                        {name} = {name}:main
                    """
                ).format(name=name, version=version)
            )

        with open(os.path.join(str(project_directory), "setup.py"), "w") as fp:
            fp.write(
                dedent(
                    """\
                    from setuptools import setup

                    setup()
                    """
                )
            )

        return str(project_directory)

    return create_project
