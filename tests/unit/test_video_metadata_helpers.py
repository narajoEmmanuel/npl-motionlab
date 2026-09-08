"""Unit tests for video metadata normalization helpers."""

import pytest

from motionlab.video_metadata import (
    _fourcc_text,
    _positive_finite_or_none,
    _reported_frame_count,
)


@pytest.mark.parametrize("value", [0.0, -1.0, float("nan"), float("inf")])
def test_positive_finite_or_none_rejects_unavailable_values(value: float) -> None:
    """Map invalid backend properties to an explicit unavailable state."""
    assert _positive_finite_or_none(value) is None


def test_reported_frame_count_requires_a_whole_value() -> None:
    """Do not silently truncate an anomalous reported frame count."""
    assert _reported_frame_count(12.0) == 12
    assert _reported_frame_count(12.5) is None


def test_fourcc_text_decodes_little_endian_property() -> None:
    """Convert the numeric OpenCV property to its four-character code."""
    numeric = sum(
        ord(character) << (8 * index)
        for index, character in enumerate("MJPG")
    )

    assert _fourcc_text(float(numeric)) == "MJPG"
