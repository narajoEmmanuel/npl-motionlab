# NPL MotionLab

MotionLab is a compact measurement-engineering project for estimating a
**2D projected sagittal-plane knee flexion angle** from controlled single-camera
smartphone video.

The project deliberately reuses mature open-source pose-estimation software
instead of rebuilding pose detection, tracking, filtering, or camera-calibration
infrastructure from scratch. MotionLab keeps the project-specific pieces that
matter for engineering traceability: source provenance, verified angle geometry,
landmark adaptation, controlled acquisition, repeatable processing, and bounded
interpretation.

## Interactive v0.2 release candidate

Interactive v0.2 adds local sessions, auditable five-landmark review, synchronized
knee/shank-foot/trunk results, and CSV/JSON/PNG/reviewed-MP4 exports. Core v0.1.0
remains the frozen measurement baseline. The local verification gate is complete;
merge, tag and release remain pending review.

Start the final backend from the repository root:

```powershell
python -m uvicorn motionlab.api.server:app --host 127.0.0.1 --port 8000
```

In a second terminal, run `npm run dev` from `apps/web`, then open
`http://127.0.0.1:5173`. See the [install and local run guide](docs/v0.2_local_run.md),
[completion evidence](docs/v0.2_completion.md), and
[release-candidate notes](docs/v0.2_release_notes.md).

## Current scope

The Core workflow is:

```text
original smartphone video
        |
        v
MotionLab source hash + metadata
        |
        v
Sports2D / RTMPose
        |
        v
pixel hip / knee / ankle landmarks
        |
        v
MotionLab verified geometry
        |
        v
2D projected knee-flexion time series
        |
        v
small controlled repeated-trial analysis
        |
        v
bounded engineering conclusion
```

**M0: Environment & Repository**, **M1: Charter & Requirements**, **M2:
Literature & Measurement Framework**, **M3: Mathematical Verification**, **M4:
Controlled Camera & Image Baseline**, **M5: Sports2D Integration**, **M6:
End-to-End Angle Pipeline**, **M7: Small Controlled Squat Dataset**, and **M8:
Final Core Analysis** are complete under the simplified Core scope.

M5 closed with a pinned isolated Sports2D environment, a tested pixel-TRC
adapter, explicit landmark mapping, preserved missingness, MotionLab-owned angle
calculation, and one representative private-video runtime checkpoint. Sports2D
exported 597 frames, MotionLab produced 541 valid geometry rows and preserved 56
`missing_landmark` rows as invalid with `NaN` projected flexion, and the full
MotionLab regression suite passed with `64 passed`.

M6 established the frozen end-to-end source-to-result workflow. The documented
command verifies source/config provenance, preserves invalid frames, and writes a
CSV, technical figure, deterministic recording-maximum summary, and provenance
JSON. The full suite passed with `73 passed`.
See [M6 reproduction and output contract](docs/m6_angle_pipeline.md).

M7 applied that frozen workflow to five independent, operator-confirmed
one-squat recordings using the right side and the predefined event rule. Source
mapping and detailed human results remain private; all five runs recorded clean
committed-code provenance, and the full suite remained at `73 passed`.
See [M7 acquisition and processing evidence](docs/m7_controlled_squat_dataset.md).

M8 validated the completed M7 artifacts and produced the bounded descriptive
analysis, missingness/failure accounting, five-trial comparison, and a
representative T01 full time series selected by lowest trial ID. The full suite
passed with `86 passed`.
See [M8 method, reproduction, and limitations](docs/m8_final_core_analysis.md).

**M9: Technical Conclusion and Release** is now in release-candidate state for
`v0.1.0`. M9 adds no new processing or analysis. It packages the final bounded
engineering conclusion, public release notes, claim boundary, and versioned
release state. See [M9 Core release report](docs/m9_core_release.md) and
[release notes](RELEASE_NOTES.md).

## Core completion path

1. review and merge the M9 release candidate;
2. confirm the complete test suite passes on the merged release state;
3. tag that final `main` commit as `v0.1.0`;
4. publish the GitHub release using `RELEASE_NOTES.md`.

No second pose engine, manual reference, full uncertainty budget, Monte Carlo
study, robustness matrix, or generalized camera calibration is required to
finish the Core.

## Final bounded conclusion

For the tested controlled workflow, MotionLab demonstrates that a small,
explicitly versioned single-camera system can transform controlled squat video
into traceable **2D projected knee-flexion** results using external pose
landmarks and independently verified MotionLab geometry.

The completed Core provides evidence for reproducible computational execution,
software traceability, and repeated operation under the tested protocol. It does
not establish pose-estimation accuracy against ground truth, anatomical 3D knee
kinematics, clinical validity, population performance, or equivalence to
professional marker-based motion capture.

## Optional work

### Post-Core video visualization

[Video Angle Overlay](docs/video_angle_overlay.md) renders existing MotionLab
CSV points and projected-flexion values on a private source video. This optional
visualization does not change the frozen Core measurement logic or conclusions.

### Kinovea reference appendix

An independent Kinovea manual-reference comparison may be added **after the Core
is complete** if it materially improves the technical report. It is not a Core
milestone and must not be described as ground truth.

### Optional Advanced MATLAB Verification Appendix

The MATLAB work remains an optional advanced verification appendix. It may be
used to demonstrate independent angle implementation, analytical verification,
deterministic sensitivity, and Python-to-MATLAB consistency. MATLAB execution
is not required for the Core release.

## Project definition

- [M9 Core release report](docs/m9_core_release.md)
- [v0.1.0 release notes](RELEASE_NOTES.md)
- [Simplified Core roadmap](docs/roadmap.md)
- [M8 final Core analysis](docs/m8_final_core_analysis.md)
- [M7 controlled squat dataset](docs/m7_controlled_squat_dataset.md)
- [M6 end-to-end angle pipeline](docs/m6_angle_pipeline.md)
- [M5 Sports2D integration audit](docs/m5_sports2d_integration.md)
- [Sports2D integration boundary](integrations/sports2d/README.md)
- [Project charter](docs/project_charter.md)
- [Engineering requirements](docs/requirements.md)
- [Controlled terminology](docs/terminology.md)
- [Targeted literature review](docs/literature_review.md)
- [Measurement framework](docs/metrology/measurement_framework.md)
- [M4 camera and image evidence](docs/metrology/camera_image_verification.md)
- [M4-D results](docs/metrology/m4d01_results.md)
- [Reuse-versus-build architecture](docs/decisions/ADR-0002-reuse-vs-build-architecture.md)
- [Simplified Core scope decision](docs/decisions/ADR-0003-simplified-core-scope.md)
- [Literature matrix](references/literature_matrix.csv)
- [Bibliography](references/references.bib)

## Engineering Foundations

The [MotionLab Engineering Foundations](docs/foundations/README.md) knowledge
base explains the mathematical, numerical, programming, and software-engineering
concepts verified through M3. These foundations remain valid and are retained.

## Environments

The MotionLab Core uses Python 3.13 and is defined by `pyproject.toml`.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

Sports2D is intentionally kept in a separate pinned environment. Installation
and execution are documented in
[`integrations/sports2d/README.md`](integrations/sports2d/README.md). It is not
a direct MotionLab package dependency.

## Claim boundary

MotionLab does not claim clinical validity, diagnostic capability, anatomical
3D knee kinematics, equivalence to professional marker-based motion capture,
pose-estimation ground-truth accuracy, or population-level performance. The
Core conclusion applies only to the explicitly tested single-camera workflow and
conditions.

Raw human video and detailed private derived artifacts remain outside the public
repository by design.
