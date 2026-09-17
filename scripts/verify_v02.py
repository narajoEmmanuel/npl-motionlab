"""Run the public MotionLab Interactive v0.2 verification commands.

This script does not run private human-data smoke tests; those remain a manual
local verification gate documented in docs/v0.2_completion.md.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "web"


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    run([sys.executable, "-m", "pytest"])
    run(["npm", "run", "test"], cwd=WEB)
    run(["npm", "run", "typecheck"], cwd=WEB)
    run(["npm", "run", "build"], cwd=WEB)
    print("Public v0.2 verification commands passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
