# Release Process

## Preparation

### Version Bump and Changelog

Bump the version in [`conscript/__init__.py`](conscript/__init__.py) and
run `tox -echangelog` to update [`CHANGES.md`](CHANGES.md). Delete any entries that aren't likely
to be useful to consumers and then open a PR with these changes and land it on
https://github.com/jsirois/conscript main.

## Release

### Push Release Tag

Sync a local branch with https://github.com/jsirois/conscript main and confirm it has
the version bump and changelog update as the tip commit:

```
$ git log --stat -1 HEAD
commit 1ce9fa95893b05bc0bc3a9a7d9c415deeb14d447 (HEAD -> main, origin/main, origin/HEAD)
Author: John Sirois <john.sirois@gmail.com>
Date:   Fri Jul 2 21:23:20 2021 -0800

    Prepare the 0.1.0 release.

 conscript/__init__.py            |   2 +-
 CHANGES.md                       |  41 +++++++
 2 files changed, 42 insertions(+), 1 deletions(-)
```

Tag the release as `v<version>` and push the tag to
https://github.com/jsirois/conscript main:

```
$ git tag --sign -am 'Release 0.1.0' v0.1.0
$ git push --tags https://github.com/jsirois/conscript HEAD:main
```

The release to PyPI is automated but requires approval from at least one team member. These
folks will all get an email with a link to the GitHub release workflow to do this. Alternatively,
they can open the Release workflow
[here](https://github.com/jsirois/conscript/actions?query=workflow%3ARelease) and
navigate to the release approval widget.

