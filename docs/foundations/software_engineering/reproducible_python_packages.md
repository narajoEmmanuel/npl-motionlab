# Reproducible Python Packages

## Purpose

MotionLab must import the same source from tests, notebooks, and future scripts
without path manipulation. Packaging makes that relationship explicit and
allows another developer to recreate generated artifacts from source.

## Core Concept

Three names serve different roles:

- repository: `npl-motionlab`;
- distribution declared in `pyproject.toml`: `npl-motionlab`;
- import package used by Python: `motionlab`.

The **src layout** places import code under `src/motionlab/`. An editable
installation links the environment to the working source so edits are visible
without reinstalling after every change.

## Intuition

The repository is the project container, the distribution is the installable
product identity, and the import package is the namespace code uses. They need
not have identical spelling. Installation is the verified bridge between them.

## Mathematical or Scientific Foundation

The reproducibility chain is:

```text
source + pyproject.toml
-> isolated .venv
-> editable installation
-> import motionlab from src/motionlab
-> tests and notebook use the same implementation
```

This is software infrastructure rather than a mathematical derivation, but it
is essential to reproducible scientific execution.

## Worked Example

`pyproject.toml` declares setuptools and discovers packages under `src`.
`src/motionlab/__init__.py` marks the import package. Installing with
`python -m pip install -e ".[dev]"` records the repository as the editable
project location; `import motionlab` then resolves to
`src/motionlab/__init__.py`.

## Connection to MotionLab

[pyproject.toml](../../../pyproject.toml) is the dependency and packaging
authority. [`src/motionlab`](../../../src/motionlab/__init__.py) contains the
package. Tests and the [M3 notebook](../../../notebooks/01_geometry_foundations.ipynb)
import `motionlab.geometry` normally, without modifying `sys.path`.

During M3, `python -m jupyter nbconvert` initially resolved a global
`jupyter-nbconvert.exe`. Its kernel could not import the editable project. The
notebook was then executed through the `.venv` executable with the environment's
`Scripts` directory first in process `PATH`. This is equivalent to using the
project environment; it is not a `PYTHONPATH` source-discovery hack.

## Assumptions

- Python satisfies the version declared in `pyproject.toml`.
- Dependencies are installed into the project `.venv`.
- Commands intended to verify the project use that environment.

## Limitations

Editable installation supports development but is not an immutable release
artifact. Reproducible dependency resolution also depends on the recorded lock
checkpoint. Correct packaging cannot guarantee scientific validity.

## Common Mistakes

- Assuming repository, distribution, and import names must match exactly.
- Importing successfully only because the current directory happens to expose
  source files.
- Adding `sys.path` or `PYTHONPATH` hacks instead of repairing installation.
- Invoking a global Jupyter command while assuming the project kernel is used.
- Committing generated `build/`, `*.egg-info/`, `.venv/`, or test caches.

## Implementation

`[build-system]` selects setuptools. `[tool.setuptools.packages.find]` points to
`src`. The empty `__init__.py` establishes the regular package. `.venv` isolates
dependencies. Generated build metadata and local environments remain ignored
because they can be regenerated from source and configuration.

## Verification

M3 confirmed the Python executable belonged to `.venv`, `motionlab.__file__`
resolved under `src/motionlab`, package metadata reported an editable project
location, tests imported successfully, and the notebook executed all five code
cells with no errors using the project environment.

## Evidence Status

- **V1:** package layout and resolution paths were inspected directly.
- **V2:** installed imports support the passing test suite and executed notebook.

## Interview Explanation

“I use a src-layout package and editable installation so imports work because
packaging is correct, not because of the working directory. When Jupyter first
resolved globally, I diagnosed executable and kernelspec resolution and ran the
project's `.venv` tool instead of adding a path hack.”

## Knowledge Check

1. How do repository, distribution, and import package names differ?
2. What problem does the src layout expose early?
3. Why is editable installation useful during development?
4. Why was the global Jupyter resolution a reproducibility problem?
5. Why should generated packaging artifacts remain outside Git?

## References

- [Project packaging configuration](../../../pyproject.toml)
- [Import package initializer](../../../src/motionlab/__init__.py)
- [Environment verification tests](../../../tests/test_environment.py)
- [Repository ignore rules](../../../.gitignore)
