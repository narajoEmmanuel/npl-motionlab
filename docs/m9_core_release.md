# M9 Core Release

## Status

**M9 release candidate prepared for v0.1.0.**

This document closes the simplified NPL MotionLab Core as a bounded
measurement-engineering workflow. It packages the evidence already completed in
M0 through M8; it does not introduce new analysis, pose processing, calibration,
or validation claims.

The final GitHub tag/release should be created only after this release candidate
is reviewed and merged to `main`.

## Engineering question and answer

The Core engineering question is whether a small, explicitly versioned
single-camera workflow can reproducibly transform controlled squat video into
traceable 2D projected knee-flexion results using external pose landmarks and
independently verified MotionLab geometry.

For the tested controlled workflow, the answer is **yes, within the documented
scope**.

The completed evidence shows that MotionLab can:

- preserve source-video identity and metadata;
- run a pinned Sports2D/RTMPose landmark workflow through an isolated boundary;
- map named hip, knee, and ankle pixel landmarks into MotionLab roles;
- compute the project-defined projected knee-flexion angle with independently
  verified MotionLab geometry;
- preserve missing or invalid geometry instead of fabricating values;
- generate traceable frame-level outputs, a deterministic event summary,
  technical figures, and provenance;
- apply the same frozen workflow to five independent controlled one-squat
  recordings;
- produce a bounded descriptive analysis of those five independent trials;
- maintain automated regression coverage through the final Core analysis.

This establishes reproducible **computational execution and traceability** for
the tested protocol. It does not establish pose-estimation accuracy or anatomical
3D validity.

## Released Core architecture

```text
controlled smartphone video
    -> source hash + metadata
    -> pinned Sports2D / RTMPose
    -> pixel hip / knee / ankle landmarks
    -> MotionLab landmark adapter
    -> verified MotionLab 2D angle geometry
    -> projected knee-flexion time series
    -> deterministic one-recording event summary
    -> five-trial descriptive analysis
    -> bounded engineering conclusion
```

Sports2D remains a replaceable external pose engine. MotionLab owns the
project-specific provenance, landmark semantics, image-domain assumptions,
invalid-data handling, angle convention, result traceability, and interpretation.

## Core evidence package

The public repository contains the reproducible implementation and documentation
needed to inspect the released Core:

- project charter and requirements;
- mathematical and software verification;
- camera/image baseline evidence;
- pinned Sports2D integration and boundary documentation;
- end-to-end angle pipeline;
- controlled five-trial acquisition/processing record;
- reproducible descriptive-analysis implementation;
- synthetic and regression tests;
- privacy rules that keep human source video and derived private artifacts out of
  Git.

Private raw video, TRCs, per-frame human results, private manifests, private
figures, hashes tied to private recordings, and machine-readable M7/M8 checkpoints
are intentionally not part of the public release.

## Reproducibility boundary

A public checkout can reproduce the MotionLab software tests and inspect all
public contracts. Reproducing the real human-video checkpoints requires the
private source recordings and their derived Sports2D artifacts.

MotionLab Core uses Python 3.13. The project package environment is declared in
`pyproject.toml`. Sports2D is deliberately isolated and pinned separately as
documented in `integrations/sports2d/README.md`.

The principal public verification command is:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

The final M8 checkpoint passed the complete suite with **86 tests**. M9 adds no
processing code and does not alter the frozen M5-M8 computational contracts.

## Released measurement convention

The primary measurand remains the **2D projected sagittal-plane knee flexion
angle** derived from projected hip, knee, and ankle roles in the image plane.

MotionLab uses the project convention:

```text
projected flexion = 180 deg - included hip-knee-ankle angle
```

Projected full extension is 0 degrees and projected flexion increases positively.
This is an image-plane measurement, not a full anatomical three-dimensional knee
joint angle.

The released event rule is:

```text
maximum_valid_projected_flexion_first_frame_v1
```

For one controlled squat recording, it selects the maximum finite valid projected
flexion and resolves an exact tie with the lowest Sports2D frame index. It does
not perform repetition segmentation, smoothing, interpolation, or anatomical
bottom-of-squat inference.

## Final Core conclusion

NPL MotionLab v0.1.0 demonstrates that a compact measurement-engineering system
can combine a mature external pose-estimation engine with a small independently
verified geometry and provenance layer to produce traceable 2D projected
knee-flexion results from controlled smartphone video.

The Core successfully progressed from analytical geometry and software tests to
a real external-engine boundary, one end-to-end representative-video checkpoint,
five independent controlled one-squat recordings, and a frozen descriptive
analysis. The same bounded workflow was retained throughout the repeated-trial
stage instead of being tuned after observing the dataset.

The result is therefore evidence for **workflow reproducibility, software
traceability, and bounded repeated execution under the tested protocol**.

It is not evidence for:

- pose-estimation accuracy against ground truth;
- anatomical 3D knee-angle accuracy;
- clinical validity or diagnostic use;
- squat quality, injury risk, or athlete-performance assessment;
- population-level performance;
- general reliability across devices, camera positions, participants, or
  environments;
- equivalence to professional marker-based motion capture.

The observed repeated-trial spread may combine real movement differences,
projected imaging effects, and pose-estimation behavior. The Core experiment does
not separate those contributions.

## Release contents and non-goals

Version `0.1.0` is the first bounded Core release. It closes M0 through M9 under
the simplified project scope.

The following remain optional or future work rather than release blockers:

- independent Kinovea comparison;
- MATLAB cross-verification appendix;
- multiple pose engines;
- generalized camera calibration;
- formal uncertainty propagation;
- robustness matrices;
- multiple participants and population inference;
- 3D reconstruction, OpenSim, inverse kinematics, or multi-camera systems.

Future work should enter the project only when it answers a concrete new
engineering question. It should not retroactively expand the claims of v0.1.0.

## Release checklist

Before publishing the final tag/release:

- [x] M0-M8 merged to `main`;
- [x] final Core analysis completed with bounded interpretation;
- [x] private human data excluded from the public repository;
- [x] release documentation and claim boundary prepared;
- [x] package version set to `0.1.0` in the release candidate;
- [ ] review and merge the M9 release candidate;
- [ ] confirm the complete test suite passes on the merged release state;
- [ ] create tag `v0.1.0` from the final `main` release commit;
- [ ] publish the GitHub release using `RELEASE_NOTES.md`.

M9 is complete only when the final release commit is tagged and the release is
published. Until then, the repository is in **M9 release-candidate** state.
