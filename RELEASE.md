# Release Process

This document describes the steps to cut a new release of `mxtifffile`.

## Steps

### 1. Bump the version

Edit the version in **both** of these files:

- `pyproject.toml` — update `version = "X.Y.Z"` in the `[project]` section
- `setup.cfg` — update `version = X.Y.Z` in the `[metadata]` section

Keep the versions in sync.

### 2. Commit and push

```bash
git add pyproject.toml setup.cfg
git commit -m "chore: bump version to X.Y.Z"
git push origin main
```

### 3. Create a GitHub Release

1. Go to the repository on GitHub.
2. Click **Releases → Draft a new release**.
3. Create a new tag matching the version (e.g. `0.0.3`).
4. Fill in the release title and notes.
5. Click **Publish release** (not "Save draft").

### 4. Automatic PyPI publish

Publishing the release triggers the `.github/workflows/python-publish.yml` workflow, which:

1. Builds the source distribution and wheel with `python -m build`.
2. Uploads them to PyPI using OIDC trusted publishing.

> **One-time setup:** The PyPI trusted publishing environment must be configured for `mxtifffile` on [pypi.org](https://pypi.org/manage/project/mxtifffile/settings/publishing/) before the first release.

### 5. Automatic conda recipe update

Publishing the release also triggers `.github/workflows/update-conda-recipe.yml`, which:

1. Fetches the SHA256 hash of the new source tarball from the PyPI JSON API.
2. Updates `meta.yaml` with the new version and SHA256.
3. Opens a pull request against `main` with the updated recipe.

Review and merge that PR so `meta.yaml` is always up to date in the repository.

## conda-forge Distribution

### First release (staged-recipes)

After the first PyPI release, submit `meta.yaml` to [conda-forge/staged-recipes](https://github.com/conda-forge/staged-recipes):

1. Fork [conda-forge/staged-recipes](https://github.com/conda-forge/staged-recipes).
2. Copy the updated `meta.yaml` into `recipes/mxtifffile/meta.yaml` in your fork.
3. Open a pull request against `conda-forge/staged-recipes`.
4. Address reviewer feedback until the PR is merged.

Once merged, the conda-forge infrastructure creates a dedicated feedstock repository (`mxtifffile-feedstock`) and publishes the package to the `conda-forge` channel.

### Subsequent releases

After the first staged-recipes PR is merged, **the conda-forge autotick bot handles future version bumps automatically**. It monitors PyPI for new releases and opens PRs against the feedstock repository. You only need to review and merge those PRs.
