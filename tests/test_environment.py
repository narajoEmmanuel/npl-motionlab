"""M0 smoke tests for the declared scientific environment."""

import importlib

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "cv2",
        "matplotlib",
        "numpy",
        "pandas",
        "plotly",
        "pydantic",
        "scipy",
        "statsmodels",
        "yaml",
    ],
)
def test_runtime_dependency_imports(module_name: str) -> None:
    """Every declared runtime dependency must be importable."""
    importlib.import_module(module_name)
