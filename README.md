# Conscript: console scripts in your own Swiss Army Knife.

[![PyPI Version](https://shields.io/pypi/v/conscript.svg)](https://pypi.org/project/conscript/)
[![License](https://shields.io/pypi/l/conscript.svg)](LICENSE)
[![Supported Pythons](https://shields.io/pypi/pyversions/conscript.svg)](pyproject.toml)
[![CI](https://github.com/jsirois/conscript/actions/workflows/ci.yml/badge.svg)](https://github.com/jsirois/conscript/actions/workflows/ci.yml)

Conscript provides a console script you can use to conveniently expose all other console scripts in
a virtual environment. In a traditional virtual environment this is of little use. In a
[zipapp](https://docs.python.org/3/library/zipapp.html), it gives you
capabilities similar to [BusyBox](https://busybox.net/).

## Use

To create a BusyBox, simply add `conscript` to your dependencies and set your application main
entrypoint to the `conscript` console script.

## Examples

Examples are probably the best way to demonstrate the utility of Conscript. Both
[Pex](https://pypi.org/project/pex/) and [Shiv](https://pypi.org/project/shiv/) are popular tools
for creating zipapps with third party dependencies; so they lead to concise examples.

### Pex

1. Create the BusyBox PEX zipapp:
    ```console
    $ pex cowsay fortune conscript --script conscript --output-file speak
    ```
2. Examine the available embedded apps:
    ```console
    $ ./speak -h
    usage: speak [-h] [PROGRAM]

    A speak busy box.

    positional arguments:
      PROGRAM     The program to execute.

                  The following programs are available:
                  + cowsay
                  + fortune

    optional arguments:
      -h, --help  Show this help message and exit.
    ```
3. Run an embedded app:
    ```console
    $ ./speak cowsay "Conscript is my Swiss Army Knife!"
      _________________________________
    | Conscript is my Swiss Army Knife! |
      =================================
                                     \
                                      \
                                        ^__^
                                        (oo)\_______
                                        (__)\       )\/\
                                            ||----w |
                                            ||     ||
    ```
4. Or another one:
    ```console
    $ ./speak fortune -h
    Usage: speak [OPTIONS] [fortune_file]

    Options:
      -h, --help     show this help message and exit
      -V, --version  Show version and exit.

    If fortune_file is omitted, fortune looks at the FORTUNE_FILE environment
    variable for the path.
    $ ./speak fortune /usr/share/fortune/science
    Nondeterminism means never having to say you are wrong.
    ```
5. Target an embedded app via a symlink:
    ```console
    $ ln -s speak cowsay
    $ ./cowsay Nifty.
      ______
    | Nifty. |
      ======
          \
           \
             ^__^
             (oo)\_______
             (__)\       )\/\
                 ||----w |
                 ||     ||
    ```

### Shiv

The capabilities exposed by Conscript are the same as in the Pex example, so this example is
abbreviated to the basics. The primary difference is that Shiv does not fully isolate requested
dependencies in the zipapp from incidental dependencies and so we see more available console
scripts than in the Pex case.

1. Create the BusyBox shiv zipapp:
    ```console
    $ shiv cowsay fortune conscript --python '/usr/bin/env python' --console-script conscript --output-file say
    Collecting cowsay
      Using cached cowsay-4.0-py2.py3-none-any.whl (24 kB)
    Collecting fortune
      Using cached fortune-1.1.0-py2.py3-none-any.whl (5.9 kB)
    Collecting conscript
      Using cached conscript-0.1.1-py2.py3-none-any.whl (7.5 kB)
    Collecting grizzled-python>=1.0
      Using cached grizzled_python-2.2.0-py2.py3-none-any.whl (36 kB)
    Installing collected packages: grizzled-python, fortune, cowsay, conscript
    Successfully installed conscript-0.1.1 cowsay-4.0 fortune-1.1.0 grizzled-python-2.2.0
    ```
2. Use it:
    ```console
    $ ./say -h
    usage: say [-h] [PROGRAM]

    A say busy box.

    positional arguments:
      PROGRAM     The program to execute.

                  The following programs are available:
                  + cowsay
                  + easy_install
                  + easy_install-3.8
                  + fortune
                  + pip
                  + pip3
                  + pip3.8
                  + shiv
                  + shiv-info

    optional arguments:
      -h, --help  Show this help message and exit.
    $ ./say cowsay --version
    4.0
    ```
