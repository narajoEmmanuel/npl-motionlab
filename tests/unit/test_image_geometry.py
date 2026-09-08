"""Unit tests for image-coordinate conversion and angle geometry."""

import math

import numpy as np
import pytest

from motionlab.geometry import angle_from_points_deg
from motionlab.image_geometry import (
    ImageSize,
    angle_from_normalized_points_deg,
    normalized_to_pixel,
)


def test_normalized_to_pixel_scales_axes_by_image_dimensions() -> None:
    """Scale x by width and y by height without rounding."""
    image_size = ImageSize(width_px=1920, height_px=1080)

    converted = normalized_to_pixel((0.25, 0.75), image_size)

    np.testing.assert_allclose(converted, (480.0, 810.0), atol=0.0)


def test_normalized_to_pixel_preserves_point_collection_shape() -> None:
    """Convert a landmark collection in one operation."""
    image_size = ImageSize(width_px=640, height_px=480)
    points = np.array([[0.0, 0.0], [0.5, 0.5], [1.0, 1.0]])

    converted = normalized_to_pixel(points, image_size)

    assert converted.shape == points.shape
    np.testing.assert_allclose(
        converted,
        [[0.0, 0.0], [320.0, 240.0], [640.0, 480.0]],
        atol=0.0,
    )


def test_normalized_to_pixel_does_not_clip_off_image_landmark() -> None:
    """Preserve raw off-image coordinates for later quality handling."""
    converted = normalized_to_pixel(
        (-0.1, 1.2),
        ImageSize(width_px=100, height_px=200),
    )

    np.testing.assert_allclose(converted, (-10.0, 240.0), atol=0.0)


@pytest.mark.parametrize(
    "invalid_coordinates",
    [
        0.5,
        (0.5,),
        (0.5, 0.5, 0.5),
        (0.5, np.nan),
        (np.inf, 0.5),
    ],
)
def test_normalized_to_pixel_rejects_invalid_coordinates(
    invalid_coordinates: object,
) -> None:
    """Reject malformed or non-finite coordinate records."""
    with pytest.raises(ValueError):
        normalized_to_pixel(
            invalid_coordinates,
            ImageSize(width_px=1920, height_px=1080),
        )


@pytest.mark.parametrize(
    ("width_px", "height_px", "exception"),
    [
        (0, 1080, ValueError),
        (1920, -1, ValueError),
        (1920.0, 1080, TypeError),
        (True, 1080, TypeError),
    ],
)
def test_image_size_rejects_invalid_dimensions(
    width_px: object,
    height_px: object,
    exception: type[Exception],
) -> None:
    """Require positive integer dimensions from the decoded image."""
    with pytest.raises(exception):
        ImageSize(width_px=width_px, height_px=height_px)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "image_size",
    [
        ImageSize(width_px=1920, height_px=1080),
        ImageSize(width_px=640, height_px=480),
        ImageSize(width_px=1080, height_px=1920),
    ],
)
def test_pixel_conversion_recovers_angle_at_multiple_aspect_ratios(
    image_size: ImageSize,
) -> None:
    """Recover a 60-degree pixel angle at landscape and portrait ratios."""
    segment_length = min(image_size.width_px, image_size.height_px) / 4.0
    vertex = np.array(
        [image_size.width_px / 2.0, image_size.height_px / 2.0]
    )
    point_a = vertex + np.array([segment_length, 0.0])
    point_c = vertex + segment_length * np.array(
        [math.cos(math.radians(60.0)), math.sin(math.radians(60.0))]
    )
    scale = np.array([image_size.width_px, image_size.height_px])
    normalized = np.array([point_a, vertex, point_c]) / scale

    computed = angle_from_normalized_points_deg(
        *normalized,
        image_size=image_size,
    )

    assert computed == pytest.approx(60.0, abs=1e-12)


def test_naive_normalized_angle_is_wrong_for_non_square_image() -> None:
    """Demonstrate the anisotropic-scale failure that ML-MOD-002 prevents."""
    image_size = ImageSize(width_px=1920, height_px=1080)
    vertex = np.array([960.0, 540.0])
    point_a = vertex + np.array([360.0, 0.0])
    point_c = vertex + 360.0 * np.array(
        [math.cos(math.radians(60.0)), math.sin(math.radians(60.0))]
    )
    scale = np.array([image_size.width_px, image_size.height_px])
    normalized = np.array([point_a, vertex, point_c]) / scale

    incorrect = angle_from_points_deg(*normalized)

    assert abs(incorrect - 60.0) > 10.0
