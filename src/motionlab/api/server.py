"""Composed MotionLab Interactive v0.2 local server.

This module keeps the established I3 app intact while registering the final
results/export routes used by the v0.2 workspace.
"""

from pathlib import Path

from .app import API_VERSION, AppContext, _frame_snapshot, app
from .completion import register_completion_routes

register_completion_routes(
    app,
    context=AppContext(Path("workspace")),
    frame_snapshot=_frame_snapshot,
    api_version=API_VERSION,
)

__all__ = ["app"]
