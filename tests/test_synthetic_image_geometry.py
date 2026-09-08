"""Image-based verification with synthetic, known planar geometry."""

import math

import cv2
import numpy as np
import pytest

from motionlab.geometry import angle_from_points_deg


def _decoded_marker_center(image: np.ndarray, intensity: int) -> np.ndarray:
    """Return the continuous (x, y) centroid of one synthetic marker."""
    rows_and_columns = np.argwhere(image == intensity)
    if rows_and_columns.size == 0:
        raise AssertionError(f"Synthetic marker {intensity} was not decoded.")
    row, column = rows_and_columns.mean(axis=0)
    return np.array([column, row])


@pytest.mark.parametrize(
    ("point_c", "expected_angle"),
    [
        ((380, 360), math.degrees(math.atan2(60, 80))),
        ((300, 400), 90.0),
        ((240, 380), math.degrees(math.atan2(80, -60))),
    ],
)
def test_lossless_raster_round_trip_preserves_known_angle(
    point_c: tuple[int, int],
    expected_angle: float,
) -> None:
    """Recover known acute, right, and obtuse angles from decoded pixels."""
    image = np.zeros((600, 800), dtype=np.uint8)
    point_a = (400, 300)
    vertex_b = (300, 300)
    cv2.circle(image, point_a, 5, 96, thickness=-1, lineType=cv2.LINE_8)
    cv2.circle(image, vertex_b, 5, 160, thickness=-1, lineType=cv2.LINE_8)
    cv2.circle(image, point_c, 5, 224, thickness=-1, lineType=cv2.LINE_8)

    encoded_ok, encoded = cv2.imencode(".png", image)
    assert encoded_ok
    decoded = cv2.imdecode(encoded, cv2.IMREAD_GRAYSCALE)
    assert decoded is not None
    assert decoded.shape == image.shape

    recovered_a = _decoded_marker_center(decoded, 96)
    recovered_b = _decoded_marker_center(decoded, 160)
    recovered_c = _decoded_marker_center(decoded, 224)
    computed = angle_from_points_deg(recovered_a, recovered_b, recovered_c)

    assert computed == pytest.approx(expected_angle, abs=1e-12)
