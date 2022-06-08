from __future__ import absolute_import

import argparse
import code
import os
import sys
from argparse import RawTextHelpFormatter
from collections import OrderedDict
from textwrap import dedent

TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Callable, Iterable

    from typing_extensions import Protocol

    # N.B.: Both `pkg_resources` and `importlib.metadata` `EntryPoint` objects have the same shape
    # (This makes sense, since importlib evolved from `pkg_resources`.).
    class EntryPoint(Protocol):
        @property
        def name(self):
            # type: () -> str
            pass

        def load(self):
            # type: () -> Callable[[], Any]
            pass


try:
    try:
        from importlib.metadata import entry_points  # type: ignore
    except ImportError:
        from importlib_metadata import entry_points  # type: ignore

    def iter_console_scripts():
        # type: () -> Iterable[EntryPoint]
        return entry_points().get("console_scripts", ())

except ImportError:
    from pkg_resources import iter_entry_points  # type: ignore

    def iter_console_scripts():
        # type: () -> Iterable[EntryPoint]
        return iter_entry_points("console_scripts")


def main():
    # type: () -> Any
    argv0 = sys.argv[0]
    exe_name = os.path.basename(argv0)
    console_scripts = OrderedDict(
        (ep.name, ep)
        for ep in sorted(iter_console_scripts(), key=lambda ep: ep.name)
        if ep.name != "conscript"
    )

    # BusyBox-style execution (dispatch based on link name):
    ep = console_scripts.get(exe_name)
    if ep:
        return ep.load()()

    # Manual entrypoint execution with extra ergonomics:
    parser = argparse.ArgumentParser(
        description="A {exe_name} busy box.".format(exe_name=exe_name),
        formatter_class=RawTextHelpFormatter,
        add_help=False,
    )
    # We jump through some hoops here with `add_help=False` and our own help flag to avoid
    # processing `-h`/`--help` automatically when a program has been specified. I.E.:
    # `busybox program -h` should forward -h to program and not display ou`r help.
    parser.add_argument(
        "-h", "--help", action="store_true", help="Show this help message and exit."
    )

    parser.add_argument(
        "program",
        metavar="PROGRAM",
        nargs="?",
        choices=list(map(str, console_scripts)),
        help=dedent(
            """\
            The program to execute.

            The following programs are available:
            + {}
            """
        ).format("\n+ ".join(console_scripts)),
    )
    args, rest = parser.parse_known_args()

    if args.program:
        ep = console_scripts[args.program]
        # Consume our sole command line argument so the underlying tool just sees argv0 and the
        # arguments bound for it.
        sys.argv.remove(args.program)
        return ep.load()()

    # There is no program being executed so now it's safe to process `-h` as our own.
    if args.help:
        parser.print_help()
        return

    # No entry point has been picked so drop to a repl.
    code.interact()


if __name__ == "__main__":
    sys.exit(main())
