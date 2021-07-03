import os
import site
import subprocess
import sys
from textwrap import dedent

from colors import bold, red  # type: ignore

import conscript

previous_tag = subprocess.check_output(args=["git", "describe", "--abbrev=0"]).decode().strip()
if conscript.__version__ in previous_tag:
    version_file = conscript.__file__
    for path in site.getsitepackages():
        if version_file.startswith(path):
            version_file = os.path.relpath(version_file, path)
            break
    sys.exit(
        bold(
            red(
                "Please increment the version in {} before running this script.".format(
                    version_file
                )
            )
        )
    )

changes = subprocess.check_output(
    args=[
        "git",
        "log",
        "--pretty=format:+ [%h](https://github.com/jsirois/conscript/commit/%h) %s",
        "HEAD...{}".format(previous_tag),
    ],
).decode()

with open("CHANGES.md") as fp:
    # Discard title and blank line following it.
    fp.readline()
    fp.readline()

    changelog = fp.read()

with open("CHANGES.md", "w") as fp:
    fp.write(
        dedent(
            """\
            # Conscript Release Notes

            ## {version}

            {changes}

            {changelog}
            """
        ).format(version=conscript.__version__, changes=changes, changelog=changelog)
    )
