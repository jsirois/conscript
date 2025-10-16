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
    **kwargs  # type: str
):
    # type: (...) -> Text
    process = subprocess.Popen(
        args=args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs
    )
    output, _ = process.communicate()
    decoded_output = output.decode("utf8")
    assert expected_returncode == process.returncode, decoded_output
    return decoded_output


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

    argv0 = (
        os.path.basename(foo_bar_conscript)
        if sys.version_info[:2] < (3, 14)
        # N.B.: Python 3.14 changed how prog is calculated.
        # For zipapps, its `sys.executable <zip>`.
        else "python3.{minor} {zipapp}".format(minor=sys.version_info[1], zipapp=foo_bar_conscript)
    )
    usage_line = "usage: {argv0} [-h] [-V]".format(argv0=argv0)

    # Ensure the usage line is rendered as 1 line.
    env = os.environ.copy()
    env["COLUMNS"] = str(max(len(usage_line) + 10, 80))

    output = get_output(args=[foo_bar_conscript, "foo", "-h"], env=env)
    assert (
        dedent(
            """\
            {usage_line}

            The foo program.

            {options_header}:
              -h, --help     show this help message and exit
              -V, --version  show program's version number and exit
            """
        ).format(usage_line=usage_line, options_header=OPTIONS_HEADER)
        == output
    ), output

    output = get_output(args=[foo_bar_conscript, "baz"], expected_returncode=2)
    assert output.startswith(
        (
            "usage: {argv0} [-h] [PROGRAM]\n"
            "{argv0}: error: argument PROGRAM: invalid choice: 'baz' (choose from {programs}"
        ).format(
            argv0=os.path.basename(foo_bar_conscript),
            programs=", ".join(
                (
                    repr(program)
                    if sys.version_info[:2] < (3, 12)
                    # N.B.: Python 3.14 dropped wrapping the choices in ''.
                    else program
                )
                for program in EXPECTED_PROGRAMS
            ),
        )
    ), output


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

    output = get_output(args=[non_program_symlink, "-h"])
    # N.B.: We insert a string of '*' and later replace these with spaces to work around `dedent`
    # stripping away significant whitespace indentation performed by the help formatter.
    assert output.startswith(
        dedent(
            """\
            usage: baz [-h] [PROGRAM]

            A baz busy box.

            positional arguments:
              PROGRAM     The program to execute.
            **************
                          The following programs are available:
                          + {programs}
            """
        )
        .replace("*", " ")
        .format(programs="\n              + ".join(EXPECTED_PROGRAMS))
    )
    assert output.endswith(
        dedent(
            """\

            {options_header}:
              -h, --help  Show this help message and exit.
            """
        ).format(options_header=OPTIONS_HEADER)
    ), output


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
    assert "foo=={}".format(FOO_VERSION) in repl_output, repl_output
    assert "bar=={}".format(BAR_VERSION) in repl_output, repl_output
