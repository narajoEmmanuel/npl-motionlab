"""Geometric measurement functions for MotionLab Interactive.

These functions remain image-plane geometry only. They do not establish clinical
joint-angle conventions or 3D anatomical meaning.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

from motionlab.geometry import angle_between_vectors_deg, angle_from_points_deg


def projected_knee_flexion_deg(
    hip: ArrayLike,
    knee: ArrayLike,
    ankle: ArrayLike,
) -> float:
    """Return MotionLab's existing projected knee-flexion convention in degrees.

    The included angle is Hip-Knee-Ankle with Knee as the vertex. MotionLab's
    released convention is 180 degrees minus that included geometric angle.
    """

    included_angle = angle_from_points_deg(hip, knee, ankle)
    return float(180.0 - included_angle)


def projected_shank_foot_angle_deg(
    knee: ArrayLike,
    ankle: ArrayLike,
    toe: ArrayLike,
) -> float:
    """Return the unsigned 2D shank-foot angle Knee-Ankle-Toe in degrees.

    The ankle is the vertex. This is intentionally a geometric image-plane
    quantity and is not labeled dorsiflexion or plantarflexion.
    """

    return float(angle_from_points_deg(knee, ankle, toe))


def projected_trunk_inclination_deg(
    hip: ArrayLike,
    shoulder: ArrayLike,
) -> float:
    """Return unsigned Hip-to-Shoulder inclination relative to image vertical.

    Image coordinates use +y downward, so the upward image-vertical reference is
    ``(0, -1)``. Both the trunk vector and the conceptual vertical ray originate
    at Hip. The returned angle is therefore 0 degrees when Hip->Shoulder points
    straight upward in the image and increases away from that direction.
    """

    hip_array = np.asarray(hip, dtype=float)
    shoulder_array = np.asarray(shoulder, dtype=float)
    if hip_array.shape != (2,) or shoulder_array.shape != (2,):
        raise ValueError("hip and shoulder must each contain exactly two coordinates")
    if not np.all(np.isfinite(hip_array)) or not np.all(np.isfinite(shoulder_array)):
        raise ValueError("hip and shoulder must contain only finite values")

    trunk_vector = shoulder_array - hip_array
    image_vertical_up = np.array([0.0, -1.0])
    return float(angle_between_vectors_deg(trunk_vector, image_vertical_up))
