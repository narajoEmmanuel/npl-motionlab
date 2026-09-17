# M7 controlled squat dataset

## Local completion checkpoint

M7 completed locally on 2026-09-16. Five independent private recordings were
processed sequentially as `M7_T01` through `M7_T05`, using the existing pinned
Sports2D runner followed by the frozen M6 angle pipeline. All five trials
produced the required CSV, angle figure, summary, and provenance JSON. The full
MotionLab suite passed once after processing: **73 passed**.

The development branch `feature/m7-controlled-squat-dataset` starts directly
from completed M6 commit `cef78d01b6267d2ab2ed9063fbdb31b7c2eaba90`.
All five processing runs record that revision and `working_tree_dirty: false`.
Their module hashes match the frozen M6 clean checkpoint at `4cc8cfa`.
No processing implementation, dependency, side, configuration, or event rule
changed. No remote Git operation was performed. M8 has not started.

## Acquisition record

The acquisition protocol remains the practical centered single-camera baseline
in [M4 camera and image evidence](metrology/camera_image_verification.md).
The operator confirmed five independent recordings, one squat per recording,
with the same phone, camera mode/lens, orientation, support, approximate
height/distance, centered sagittal framing, and lighting setup.

This setup compliance is operator-reported, not an independent measurement of
camera positioning. Exact device/settings and acquisition date were not supplied;
the manifest keeps the acquisition date null. Filesystem dates are not treated
as capture dates. Trial IDs are a stable filename mapping, not an inferred
chronological order. Originals retain their filenames and remain unchanged.
All five source SHA-256 values are distinct.

## Frozen processing contract

- External Sports2D `0.8.34`, Pose2Sim `0.10.49`, Python 3.13.
- `Body_with_feet`, `balanced`, one person, highest-likelihood ordering.
- Pixel TRC boundary; no interpolation, filtering, outlier rejection,
  metre conversion, C3D, augmentation, IK, or Sports2D angle calculation.
- Right-side landmarks by name: `RHip`, `RKnee`, `RAnkle`.
- MotionLab geometry computes projected flexion as `180 - included_angle`.
- Event rule: `maximum_valid_projected_flexion_first_frame_v1`.

The complete configuration remains in the existing
[Sports2D runner](../integrations/sports2d/run_sports2d.py), and the output/event
contract remains in [M6 documentation](m6_angle_pipeline.md). The known upstream
TRC unit-header limitation remains documented in the
[M5 integration evidence](m5_sports2d_integration.md); TRCs were not rewritten.

## Private evidence and reproduction

All evidence is under ignored `data/raw/` and `data/derived/` paths:

```text
data/raw/m7/                         original recordings
data/derived/m7/trial_manifest.json  source mapping and per-trial checkpoints
data/derived/m7/M7_T01/              repeated through M7_T05
    source_metadata.json
    sports2d_console.log
    sports2d/<original-stem>_Sports2D/
        <original-stem>_Sports2D_px_person00.trc
        motionlab_sports2d_provenance.json
    motionlab_console.log
    motionlab/
        knee_flexion.csv
        knee_flexion.png
        summary.json
        provenance.json
```

The private manifest records source identity/hash, acquisition confirmation,
selected side, engine versions/model/mode, TRC and engine-provenance paths,
processing status, row counts/reasons, event result, output directory, and
MotionLab revision/dirty flag. Private hashes and numerical results are not
copied into public documentation.

To reproduce a trial, select its original source from the private manifest,
choose a new unused trial output root, and invoke the existing commands:

```powershell
$source = 'data\raw\m7\<original-filename>'
$trialRoot = 'data\derived\m7\<new-unused-trial-directory>'
& "$env:USERPROFILE\.venv\sports2d-motionlab\Scripts\python.exe" `
    integrations\sports2d\run_sports2d.py $source `
    --result-dir "$trialRoot\sports2d"

# Use the exact paths produced by the runner above.
$trc = '<new-pixel-TRC-path>'
$engineProvenance = '<new-motionlab_sports2d_provenance.json-path>'
& .\.venv\Scripts\python.exe -m motionlab.angle_pipeline $source `
    --trc $trc --engine-provenance $engineProvenance `
    --side right --output-dir "$trialRoot\motionlab"
```

Process T01 through T05 sequentially, checking each output before proceeding.
Do not overwrite the completed checkpoint directories.

## Verification and decision

For each trial, source/TRC/engine-provenance hashes were checked against the
actual inputs, the complete runner configuration was compared with engine
provenance, and frozen module hashes were checked against M6. CSV frame order,
row counts, and selected pixel coordinates match the input TRC. Valid flexion
is finite; invalid flexion must remain NaN with its explicit reason. These five
runs contain no invalid geometry rows, so they do not independently exercise
missingness; the preserved M5 runtime evidence and regression suite cover it.
Each summary's maximum and first-frame tie rule were checked against its CSV.

| Trial | Processing and boundary verification |
|---|---|
| M7_T01 | Complete |
| M7_T02 | Complete |
| M7_T03 | Complete |
| M7_T04 | Complete |
| M7_T05 | Complete |

**M7 COMPLETE locally.** This demonstrates traceable operation on five
operator-confirmed controlled recordings. It does not establish pose accuracy,
clinical validity, anatomical 3D kinematics, or population performance.
Cross-trial descriptive analysis and conclusions remain for M8.
