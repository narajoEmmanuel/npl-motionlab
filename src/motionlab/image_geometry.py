"""Image-coordinate operations used by MotionLab.

Normalized landmark coordinates must be converted to a common physical image
scale before Euclidean geometry is evaluated. This module treats pixel
coordinates as continuous image coordinates; it does not round them to array
indices or clip landmarks that fall outside the image.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from motionlab.geometry import angle_from_points_deg


@dataclass(frozen=True)
class ImageSize:
    """Positive image dimensions in pixels."""

    width_px: int
    height_px: int

    def __post_init__(self) -> None:
        """Reject dimensions that cannot describe a decoded image."""
        for name, value in (
            ("width_px", self.width_px),
            ("height_px", self.height_px),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer.")
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero.")


def normalized_to_pixel(
    coordinates: ArrayLike,
    image_size: ImageSize,
) -> np.ndarray:
    """Convert normalized image coordinates to continuous pixel coordinates.

    The final array axis must contain ``(x, y)``. Leading dimensions are
    preserved, so the function accepts either one point or a collection of
    points. Values outside ``[0, 1]`` are retained because pose estimators can
    report off-image landmarks and silently clipping them would alter the raw
    measurement.
    """
    points = np.asarray(coordinates, dtype=float)

    if points.ndim == 0 or points.shape[-1] != 2:
        raise ValueError(
            "coordinates must have a final axis of length two for (x, y)."
        )
    if not np.all(np.isfinite(points)):
        raise ValueError("coordinates must contain only finite values.")

    scale = np.array([image_size.width_px, image_size.height_px], dtype=float)
    return points * scale


def angle_from_normalized_points_deg(
    a: ArrayLike,
    b: ArrayLike,
    c: ArrayLike,
    image_size: ImageSize,
) -> float:
    """Return angle ABC after converting normalized points to pixels."""
    pixel_points = normalized_to_pixel([a, b, c], image_size)
    return angle_from_points_deg(*pixel_points)
