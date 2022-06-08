from __future__ import absolute_import

import os
import subprocess
import sys
from textwrap import dedent

import pytest  # type: ignore

TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, List, Text

    from conftest import CreateConscript, CreateProject


FOO_VERSION = "1.0.0"


@pytest.fixture(scope="module")
def foo_project_dir(create_project):
    # type: (CreateProject) -> str
    return create_project("foo", FOO_VERSION)


BAR_VERSION = "42"


@pytest.fixture(scope="module")
def bar_project_dir(create_project):
    # type: (CreateProject) -> str
    return create_project("bar", BAR_VERSION)


@pytest.fixture(scope="module")
def foo_bar_conscript(
    create_conscript,  # type: CreateConscript
    foo_project_dir,  # type: str
    bar_project_dir,  # type: str
):
    # type: (...) -> str
    return create_conscript([foo_project_dir, bar_project_dir])


def get_output(
    args,  # type: List[str]
    expected_returncode=0,  # type: int
):
    # type: (...) -> Text
    process = subprocess.Popen(args=args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, _ = process.communicate()
    assert expected_returncode == process.returncode
    return output.decode("utf8")


def assert_version(
    args,  # type: List[str]
    expected_version,  # type: str
):
    # type: (...) -> None
    output = get_output(args=args + ["--version"])
    assert expected_version == output.strip()


# N.B.: Conscript depends on setuptools for Python <= 3.5 for pkg_resources.iter_entry_points and
# that dependency introduces two easy_install console scripts.
EXPECTED_PROGRAMS = sorted(
    ["foo", "bar"]
    + (["easy_install", "easy_install-3.8"] if sys.version_info[:2] <= (3, 5) else [])
)


OPTIONS_HEADER = "optional arguments" if sys.version_info[:2] < (3, 10) else "options"


def test_conscript(foo_bar_conscript):
    # type: (str) -> Any
    assert_version(args=[foo_bar_conscript, "foo"], expected_version=FOO_VERSION)
    assert_version(args=[foo_bar_conscript, "bar"], expected_version=BAR_VERSION)

    assert (
        dedent(
            """\
            usage: {argv0} [-h] [-V]

            The foo program.

            {options_header}:
              -h, --help     show this help message and exit
              -V, --version  show program's version number and exit
            """
        ).format(options_header=OPTIONS_HEADER, argv0=os.path.basename(foo_bar_conscript))
        == get_output(args=[foo_bar_conscript, "foo", "-h"])
    )

    assert (
        "usage: {argv0} [-h] [PROGRAM]\n"
        "{argv0}: error: argument PROGRAM: invalid choice: 'baz' (choose from {programs})\n"
    ).format(
        argv0=os.path.basename(foo_bar_conscript),
        programs=", ".join("'{}'".format(program) for program in EXPECTED_PROGRAMS),
    ) == get_output(
        args=[foo_bar_conscript, "baz"], expected_returncode=2
    )


def test_busybox(foo_bar_conscript):
    # type: (str) -> Any
    basedir = os.path.dirname(foo_bar_conscript)

    foo_symlink = os.path.join(basedir, "foo")
    os.symlink(foo_bar_conscript, foo_symlink)
    assert_version(args=[foo_symlink], expected_version=FOO_VERSION)

    bar_symlink = os.path.join(basedir, "bar")
    os.symlink(foo_bar_conscript, bar_symlink)
    assert_version(args=[bar_symlink], expected_version=BAR_VERSION)

    non_program_symlink = os.path.join(basedir, "baz")
    os.symlink(foo_bar_conscript, non_program_symlink)
    # N.B.: We insert a string of '*' and later replace these with spaces to work around `dedent`
    # stripping away significant whitespace indentation performed by the help formatter.
    assert (
        dedent(
            """\
            usage: baz [-h] [PROGRAM]

            A baz busy box.

            positional arguments:
              PROGRAM     The program to execute.
            **************
                          The following programs are available:
                          + {programs}

            {options_header}:
              -h, --help  Show this help message and exit.
            """
        )
        .replace("*", " ")
        .format(
            programs="\n              + ".join(EXPECTED_PROGRAMS), options_header=OPTIONS_HEADER
        )
        == get_output(args=[non_program_symlink, "-h"])
    )


def test_repl(foo_bar_conscript):
    # type: (str) -> Any
    process = subprocess.Popen(
        args=[foo_bar_conscript],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output, _ = process.communicate(
        input=dedent(
            """\
            from foo import __version__ as foo_version
            from bar import __version__ as bar_version

            print("foo=={}".format(foo_version))
            print("bar=={}".format(bar_version))
            """
        ).encode("utf8")
    )
    repl_output = output.decode("utf8")
    assert "foo=={}".format(FOO_VERSION) in repl_output
    assert "bar=={}".format(BAR_VERSION) in repl_output
