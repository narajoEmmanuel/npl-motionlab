"""Versioned semantic measurement definitions for MotionLab Interactive."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

import numpy as np
from numpy.typing import ArrayLike

from .geometry import (
    projected_knee_flexion_deg,
    projected_shank_foot_angle_deg,
    projected_trunk_inclination_deg,
)


@dataclass(frozen=True)
class MeasurementDefinition:
    name: str
    display_name: str
    version: str
    unit: str
    dependencies: tuple[str, ...]
    calculator: Callable[..., float]


@dataclass(frozen=True)
class MeasurementResult:
    definition_name: str
    definition_version: str
    value_deg: float | None
    valid: bool
    invalid_reason: str | None


KNEE_FLEXION = MeasurementDefinition(
    name="projected_knee_flexion",
    display_name="2D projected knee flexion",
    version="1",
    unit="deg",
    dependencies=("hip", "knee", "ankle"),
    calculator=projected_knee_flexion_deg,
)

SHANK_FOOT_ANGLE = MeasurementDefinition(
    name="projected_shank_foot_angle",
    display_name="2D projected shank-foot angle",
    version="1",
    unit="deg",
    dependencies=("knee", "ankle", "toe"),
    calculator=projected_shank_foot_angle_deg,
)

TRUNK_INCLINATION = MeasurementDefinition(
    name="projected_trunk_inclination",
    display_name="2D projected trunk inclination",
    version="1",
    unit="deg",
    dependencies=("hip", "shoulder"),
    calculator=projected_trunk_inclination_deg,
)

DEFINITIONS = {
    definition.name: definition
    for definition in (KNEE_FLEXION, SHANK_FOOT_ANGLE, TRUNK_INCLINATION)
}


def definitions_for_landmark(role: str) -> tuple[MeasurementDefinition, ...]:
    """Return only measurements affected by one semantic landmark role."""

    return tuple(
        definition
        for definition in DEFINITIONS.values()
        if role in definition.dependencies
    )


def evaluate_measurement(
    definition_name: str,
    landmarks: Mapping[str, ArrayLike],
) -> MeasurementResult:
    """Evaluate one measurement from semantic landmarks with explicit validity.

    Missing/non-finite dependencies are reported as ``missing_landmark``.
    Zero-length segment geometry is reported as ``degenerate_geometry``.
    """

    if definition_name not in DEFINITIONS:
        raise ValueError(f"Unknown measurement definition: {definition_name}")

    definition = DEFINITIONS[definition_name]
    points: list[np.ndarray] = []
    for role in definition.dependencies:
        if role not in landmarks:
            return MeasurementResult(
                definition.name,
                definition.version,
                None,
                False,
                "missing_landmark",
            )
        try:
            point = np.asarray(landmarks[role], dtype=float)
        except (TypeError, ValueError):
            return MeasurementResult(
                definition.name,
                definition.version,
                None,
                False,
                "missing_landmark",
            )
        if point.shape != (2,) or not np.all(np.isfinite(point)):
            return MeasurementResult(
                definition.name,
                definition.version,
                None,
                False,
                "missing_landmark",
            )
        points.append(point)

    try:
        value = float(definition.calculator(*points))
    except ValueError:
        return MeasurementResult(
            definition.name,
            definition.version,
            None,
            False,
            "degenerate_geometry",
        )

    return MeasurementResult(
        definition.name,
        definition.version,
        value,
        True,
        None,
    )
