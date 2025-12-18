# Kognic Base Clients

Python 3 library providing base API clients. This package is used by other Kognic Python packages such as [kognic-io](https://pypi.org/project/kognic-io/).
This package is public and available on [PyPi](https://pypi.org/project/kognic-base-clients/).

## Installation

To install the latest public version, run `pip install kognic-base-clients`.

For local development it is recommended to install locally with `pip install -e .` in the root folder.

## Releasing

Releasing new versions of the package is done by creating a git tag. This will trigger a GitHub action that will build
and publish the package to PyPi. The version number is determined by the git tag, so make sure to use the correct format
when creating a new tag. The format is `vX.Y.Z` where `X`, `Y` and `Z` are integers. To create a new tag and push it to
the remote repository, run the following commands

```bash
git tag vX.Y.Z; git push origin vX.Y.Z
```

**Important:** Don't forget to update the changelog with the new version number and a description of the changes before
releasing a new version. The changelog is located in the root folder and is named `CHANGELOG.md`.