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
    args=["git", "log", "--oneline", "--no-decorate", "HEAD...{}".format(previous_tag)],
).decode()

with open("CHANGES.md", "a") as fp:
    fp.write(
        dedent(
            """\
            ## {version}

            {changes}
            """
        ).format(
            version=conscript.__version__,
            changes=os.linesep.join("+ {}".format(line) for line in changes.splitlines()),
        )
    )
