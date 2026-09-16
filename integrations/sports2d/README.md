# Sports2D integration boundary

This directory defines the external pose-engine side of MotionLab M5.
Sports2D is deliberately kept out of the MotionLab `pyproject.toml` environment.
MotionLab consumes its file output rather than importing the pose stack.

## Pinned versions

- Sports2D `0.8.34`
- Pose2Sim `0.10.49`
- Python `3.13`
- Sports2D pose model: `Body_with_feet`
- Sports2D mode: `balanced`

The versions above were selected and reviewed on 2026-09-16.

## Why an isolated environment

Sports2D is a mature external workflow with its own inference and Pose2Sim
stack. Keeping it separate prevents that dependency surface from destabilizing
the small tested MotionLab package. Sports2D 0.8.34 also changes process-wide
state while loading its processing module, which is another reason not to make
it a direct MotionLab import.

The integration contract is therefore:

```text
original video
  -> isolated Sports2D 0.8.34 process
  -> *_Sports2D_px_person00.trc
  -> MotionLab sports2d_adapter
  -> MotionLab verified geometry
```

## Install on Windows

Install `uv` if it is not already available, then create the external
environment outside this repository:

```powershell
uv venv "$env:USERPROFILE\.venv\sports2d-motionlab" --python 3.13
& "$env:USERPROFILE\.venv\sports2d-motionlab\Scripts\Activate.ps1"
uv pip install -r integrations\sports2d\requirements.txt
```

Confirm the pinned versions:

```powershell
python -c "from importlib.metadata import version; print(version('sports2d')); print(version('Pose2Sim'))"
```

## Run

Keep human video private, for example under `data/raw/`. Run:

```powershell
python integrations\sports2d\run_sports2d.py `
  data\raw\<video>.mp4 `
  --result-dir data\derived\sports2d
```

The runner uses one person, noninteractive highest-likelihood person selection,
`Body_with_feet`, balanced mode, pixel pose output, and no MotionLab-irrelevant
angle calculation. Interpolation, Hampel outlier rejection, and trajectory
filtering are disabled.

The expected landmark file is inside:

```text
data/derived/sports2d/<video>_Sports2D/
    <video>_Sports2D_px_person00.trc
```

A `motionlab_sports2d_provenance.json` file is also written there. It includes
the source-video SHA-256 hash, engine versions, selected pose configuration,
and the file-contract limitations used by MotionLab.

## M5 coordinate contract

For `Body_with_feet`, MotionLab maps by marker name:

| Side | Hip | Knee | Ankle |
|---|---|---|---|
| Right | `RHip` | `RKnee` | `RAnkle` |
| Left | `LHip` | `LKnee` | `LAnkle` |

MotionLab reads TRC X/Y values as pixels and does not rescale them. The TRC Z
column is retained by the parser but is not used by the 2D angle calculation.

Sports2D applies its configured confidence thresholds before exporting the pose.
Low-confidence landmarks can therefore appear as missing/NaN coordinates. The
standard pixel TRC used here does not preserve confidence scores, so M5 does not
claim access to raw detector confidence.

The Sports2D TRC `Time` field is engine-derived. MotionLab preserves it but does
not treat it as independently verified source-video timing.

## Angle ownership

Sports2D angle calculation is disabled. The authoritative project result is
computed later from the pixel hip/knee/ankle coordinates with MotionLab's
existing verified geometry and projected-flexion convention.

## Runtime checkpoint

M5 source integration can be reviewed and unit-tested without model inference.
M5 is not complete until the pinned external environment is installed locally
and produces at least one expected pixel TRC file from a representative private
video, and that file is successfully ingested by MotionLab.
