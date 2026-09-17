# M8 Final Core Analysis

## Purpose and completed input

M8 is the bounded descriptive analysis of the five independent,
operator-confirmed one-squat recordings completed in M7. It asks what event
results and between-trial spread the same frozen computational workflow
produced under that acquisition protocol. The five recordings, not their
individual frames, are the five analysis units.

The authoritative index is private `data/derived/m7/trial_manifest.json`.
The exact trial set is `M7_T01`, `M7_T02`, `M7_T03`, `M7_T04`, and `M7_T05`.
Analysis reads their existing `motionlab/summary.json`, `provenance.json`, and
`knee_flexion.csv`; numerical values are not copied from documentation or
hard-coded into the module. Sports2D and M6 were not rerun.

## Frozen contract and integrity checks

Processing remains Sports2D 0.8.34 / Pose2Sim 0.10.49, Body_with_feet / balanced,
one highest-likelihood person, and right-side RHip/RKnee/RAnkle pixel landmarks.
No interpolation, filtering, outlier rejection, metre conversion, Sports2D
angle calculation, augmentation, or IK is enabled. MotionLab geometry remains
the angle authority. M6 and M7 processing code and documentation are unchanged.

The primary variable is the existing `maximum_projected_flexion_deg` from
`maximum_valid_projected_flexion_first_frame_v1`. Analysis does not change the
metric, winning frame, segmentation, or curve.

Before statistics, the module requires exactly five unique expected trial IDs,
complete status, distinct source hashes, consistent manifest/summary events,
right side, pinned engine versions/model/mode, compatible M6 provenance, and
all four nonempty M6 outputs. It checks actual source/TRC/engine hashes, the
complete engine overrides against the frozen runner's configuration, and CSV
counts, invalid reasons/NaNs, frame order, and the existing event rule.
Any mismatch raises an error before outputs are written; trials are never
silently repaired or excluded.

Historical module hashes are verified against the recorded Git revision, and
current module content must match that historical content. Git on this Windows
checkout converted `angle_pipeline.py` from LF to CRLF when switching branches:
its raw checkout hash differs, while the original M7 LF hash matches historical
content exactly. Compatibility explicitly allows only LF/CRLF checkout
conversion. Recorded M7 hashes and artifact bytes are not altered.

See the frozen [M6 contract](m6_angle_pipeline.md) and
[M7 acquisition record](m7_controlled_squat_dataset.md).

## Descriptive calculation and accounting

`motionlab.trial_analysis.descriptive_statistics` calculates only:

- number of trials, n;
- arithmetic mean;
- sample standard deviation with `ddof=1` (denominator n minus 1);
- minimum and maximum;
- range, maximum minus minimum.

The convention is explicit in both summary and provenance. No confidence
intervals, inferential statistics, reliability metrics, uncertainty propagation,
or additional descriptive metrics are added.

Accounting reports successful trial count, pipeline failure count, invalid rows
per trial and in total, invalid-reason counts, and required-output presence.
A completed analysis requires all five successful inputs; an incomplete or
failed input stops analysis rather than yielding an aggregate over fewer trials.
All five inputs here were complete, all required outputs were present, and no
invalid geometry rows or pipeline failures were observed.

## Private artifacts and figures

The demonstrated checkpoint is `data/derived/m8/clean_da17654/`:

| Artifact | Definition |
|---|---|
| `trial_event_summary.csv` | Trial ID, total/valid/invalid rows, existing event frame/time/flexion, and processing status; no source identity/hash |
| `descriptive_summary.json` | Six descriptive quantities, fixed contract, and missingness/failure accounting |
| `trial_maxima.png` | Five points by trial ID; maximum observed 2D projected knee flexion in degrees; no fitted lines or intervals |
| `representative_timeseries.png` | Full T01 projected flexion versus Sports2D frame; NaNs and absent frames break the curve; no smoothing/interpolation |
| `analysis_provenance.json` | Schema, analysis Git revision/dirty status, manifest path/hash, trial IDs, side/rule/SD convention, input hashes, module hashes, output names |

T01 is representative solely because it has the lowest trial ID, independent
of its outcome. Both figures were visually inspected at the real checkpoint:
labels and units are readable, all five points appear, and the T01 frame span
is complete.

Raw sources, TRCs, per-frame data, manifests, private hashes, numerical summaries,
and figures stay under ignored `data/raw/` or `data/derived/`; none is committed.
Public documentation describes the method and bounded status. Numerical results
remain in the private machine-readable checkpoint; publication scope is not
expanded for a future M9 release.

## Reproduction and provenance

From the repository root using the existing MotionLab environment:

```powershell
& .\.venv\Scripts\python.exe -m motionlab.trial_analysis `
    data\derived\m7\trial_manifest.json `
    --output-dir data\derived\m8\<new-unused-directory>
```

Use a new output directory; existing output files are not overwritten. Relative
paths within the M7 manifest resolve from the repository root. The command
requires private local M7 evidence and its historical Git commit; a public
checkout alone does not contain the human dataset.

The real run recorded Git revision
`da176541c76387612902ec3d42310a9dd3f00b16` and
`working_tree_dirty: false`. Its provenance includes the actual manifest hash,
each trial's summary/provenance/CSV/figure hashes, the analysis module hash, and
current frozen-module byte hashes. Later documentation-only commits do not
change the code used by this checkpoint.

Focused synthetic tests passed: **13 passed**. They cover known mean/sample
SD/extrema/range, incompatible inputs, invalid-value preservation, verified Git
line-ending conversion, CLI/output schema, and overwrite prevention. No private
data is used in tests. The full suite passed once after the real analysis:
**86 passed** (73 existing plus 13 M8 tests).

## Bounded technical conclusion and decision

The same frozen workflow processed all five controlled recordings successfully.
Their predefined event summaries have the observed mean, sample SD, extrema,
and range recorded in the private descriptive summary. No invalid geometry rows
or pipeline failures were observed in these five recordings. This demonstrates
traceable computational execution and describes the observed within-protocol
spread for this small dataset.

That spread can combine differences in movement, projected imaging, and pose
estimation; this experiment cannot separate those contributions. Setup compliance
and one-squat independence are operator-confirmed. Engine timestamps are not
independently verified source timestamps. The five zero-invalid trials do not
test missing-landmark robustness, and sample SD is not an accuracy or uncertainty
estimate. There is no ground-truth comparison or population sampling.

M8 does not establish pose accuracy, anatomical 3D knee flexion, clinical
validity, squat quality, population performance, general reliability/robustness,
or equivalence to motion capture.

**M8 COMPLETE locally.** No remote Git operations, releases, tags, optional
Kinovea/MATLAB work, or M9 work were performed during M8. M9 remains planned.
