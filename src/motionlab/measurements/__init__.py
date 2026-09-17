"""Measurement definitions for NPL MotionLab Interactive."""

from .definitions import (
    DEFINITIONS,
    KNEE_FLEXION,
    SHANK_FOOT_ANGLE,
    TRUNK_INCLINATION,
    MeasurementDefinition,
    MeasurementResult,
    evaluate_measurement,
)
from .geometry import (
    projected_knee_flexion_deg,
    projected_shank_foot_angle_deg,
    projected_trunk_inclination_deg,
)

__all__ = [
    "DEFINITIONS",
    "KNEE_FLEXION",
    "SHANK_FOOT_ANGLE",
    "TRUNK_INCLINATION",
    "MeasurementDefinition",
    "MeasurementResult",
    "evaluate_measurement",
    "projected_knee_flexion_deg",
    "projected_shank_foot_angle_deg",
    "projected_trunk_inclination_deg",
]
