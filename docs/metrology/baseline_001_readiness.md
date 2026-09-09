# baseline_001: real acquisition readiness evidence

## Evidence and scope

This public-safe summary registers a real M4-C acquisition and exploratory
M4-D manual digitization sensitivity. M4 remains incomplete. Original video,
frame, acquisition record, and coordinate records remain private and unchanged.
No pose estimation or M5 work is involved.

The supplied source SHA-256 was checked locally against the original file and
matched. The retained PNG was pixel-identical to the first frame decoded during
review with OpenCV 5.0.0. Four private A/B/C coordinate records were recalculated
using the verified `motionlab.geometry.angle_from_points_deg`; all four matched
their saved angles. This verifies the coordinate-to-angle arithmetic, not the
physical correctness of the manually selected centers.

| Quantity | Observation and evidential meaning |
|---|---|
| Nominal target | Half-scale 3-4-5: BA 150 mm, BC 200 mm, AC 250 mm; nominal ABC 90 degrees |
| Physical measurement | User reports the same center-to-center dimensions measured manually with a ruler; instrument resolution and construction/measurement uncertainty unquantified; no independently calibrated 90-degree angle |
| Acquisition | User reports landscape, static throughout, downloaded from iCloud without intentional editing/transcoding; requested resolution and FPS unknown |
| Decoded file | 3840 × 2160, HEVC, FFMPEG backend, reported count 262 and nominal FPS 55.528081949841045 |
| Orientation | Backend reports 180 degrees; user did not observe an obviously inverted display. Review decoder reports automatic orientation enabled. This does not establish physical camera rotation or original extraction settings |
| Timing | Count/FPS gives 4.718333333333334 seconds only as a derived duration; CFR/VFR, actual timestamps and dropped-frame behavior remain unresolved |

No new decoder dependency is warranted for the present static-frame decision.
The bundled FFMPEG backend is already used by OpenCV; no external ffmpeg,
ffprobe, or PyAV workflow has been added.

## Manual localization results

Four separate manual digitizations of one frame gave, in degrees:
89.7296028466422, 89.82244597715874, 90.5589654808322, 89.0683846982529.

| Statistic | Degrees |
|---|---:|
| Mean image-derived ABC | 89.794850 |
| Mean signed difference from nominal 90 | -0.205150 |
| Sample standard deviation (denominator n − 1) | 0.610094 |
| Range (maximum − minimum) | 1.490581 |
| Mean absolute difference from nominal 90 | 0.484633 |

The observational unit here is a digitization, with four digitizations nested
within one frame from one acquisition. These are not four independent camera
trials. The spread is exploratory manual digitization repeatability/sensitivity,
not total camera uncertainty. The mean difference is not camera bias, and the
absolute difference is not validated accuracy. Comparison combines target
construction, physical measurement resolution, projection, optics, decoding,
and manual localization. Do not use these results to set a pass/fail threshold.

The existing untracked manual picker was inspected but not changed or executed.
It displays a 1600-pixel-wide version of the 3840-pixel image and maps integer
clicks back by a common scale: one display-pixel step corresponds to 2.4 source
pixels for this frame. That is sampling granularity, not an uncertainty estimate.
Its angle implementation is separate from the verified library; recalculation
above independently checked these records. It has a hard-coded output and can
overwrite an earlier record. It does not record operator, tool version, or
display conditions. Preserve it as user work; do not include it accidentally in
a documentation commit or treat it as a characterized measurement instrument.

The summary can be reproduced without publishing coordinate records: for each
of the four private JSON records read `points_px` in A, B, C order, recalculate
ABC with `angle_from_points_deg`, and check against `angle_ABC_deg`. Compute
the arithmetic mean, mean of (ABC − 90), sample standard deviation with n − 1,
max minus min, and mean of abs(ABC − 90). The four values above also suffice
to reproduce the aggregate statistics; private paths and coordinates need not
be included in a public artifact.

## Record gaps before the controlled sequence

The private acquisition YAML has unindented child fields: `device`,
`requested_capture`, and `physical_setup` parse as null rather than mappings.
Its referenced target companion file is absent. Preserve the original and
prepare a separately named corrected record from the existing template,
documenting the correction and linking back to the original. Add the target
layout, A/B/C identities, asymmetric mark, ruler method/resolution if known,
and construction/flatness notes. Unknown historical settings stay unknown.

Support, room clearance, distance, height, yaw/pitch/roll assessment, lens/zoom,
and setting controllability are not established by the available record. Capture
time/operator and app/OS details also remain incomplete. These gaps do not erase
baseline_001 evidence, but prevent freezing an executable physical protocol.
Identify a reproducible current configuration before new trials; if the original
configuration cannot be recovered, call it a new setup rather than assuming it
matches baseline_001.

## Smallest proposed M4-D sequence: horizontal image position

This sequence has now been executed and analyzed. See
[M4-D horizontal image-position results](m4d01_results.md). The text below
preserves the design specified before outcome angles were inspected.

Purpose: assess whether centering the target versus a right-of-center location
materially changes the planar-angle observation for a provisional M9 framing
choice. This is a bounded exploratory screen, not a lens-distortion calibration
or a complete field map. Keep all other controllable factors fixed.

Proposed levels are B at (x/W, y/H) = (0.50, 0.50) for C and (0.75, 0.50)
for R. At 3840 × 2160 these aim points are (1920, 1080) and (2880, 1080).
Use them as placement instructions, not acceptance tolerances; record achieved
locations. The baseline marker spans suggest the three centers can fit at both
positions, but room clearance and visibility of the complete target/mark still
need checking. Translate the target laterally in the same physical plane with
the phone fixed. Do not pan the phone, tilt the target, resize/crop digitally,
or change depth to achieve placement. Lateral slant distance changes naturally;
keep perpendicular camera-to-plane distance constant and report the distinction.

This proposal is conditional on a stable support and planar translation being
feasible. Confirm those constraints and record the chosen configuration plus
these levels/counts in a dated private plan before computing any M4-D outcome
angles. If infeasible, revise the plan before acquisition/analysis rather than
silently changing levels. No numerical yaw, pitch, roll, height, or distance
factor levels are justified by the available setup information.

| Order | Capture IDs | Condition | Count |
|---|---|---|---:|
| 1–3 | m4d01_C_01, m4d01_C_02, m4d01_C_03 | Center; separate start/stop recordings without moving the setup | 3 |
| 4–6 | m4d01_R_01, m4d01_R_02, m4d01_R_03 | Translate to right level once, then separate recordings without moving | 3 |
| 7 | m4d01_C_return_01 | Return to center; final drift/return check | 1 |

Seven captures are a project-defined practical first screen, not a powered
design. Three start/stop trials per main level describe within-session recording
repeatability, not independent setup repositioning. The single return is only
a diagnostic. Order/time effects remain a limitation.

Use capture IDs in a private manifest mapping to untouched original filenames
and SHA-256 values. Name sidecars `<capture_id>_metadata.json`,
`<capture_id>_acquisition.yaml`, `<capture_id>_frame_000.png`, and
`<capture_id>_digitization_01.json` through `_04.json`. Never overwrite a source
or prior record. All originals, derivatives and private metadata stay in the
Git-ignored raw-data area. Raw filenames need not be renamed to match IDs.

Hold constant: phone/app, selected lens/zoom, resolution/FPS mode, landscape
orientation, stabilization/HDR state, support, camera orientation/height,
target plane/depth and orientation, marker identities, lighting, and the
focus/exposure/white-balance policy. Record uncontrollable automatic behavior.
If settings differ from baseline_001, use the new center captures as the
comparison baseline. Do not infer requested FPS from the reported 55.528 value.

Settle the setup before recording and retain a stationary interval. Use the
first decoded frame if all centers and the asymmetric mark/outline are clear;
otherwise document the quality failure before calculating an angle. Use four
fresh A/B/C digitizations per retained frame with the same display scale,
operator, tool and center rule, hiding previous picks/results. Retain all raw
coordinates. Verify angles with the existing library. Summarize each capture's
four picks first, then compare the three C and three R capture means and show
within-frame spread separately. Do not pool clicks into independent trials.
Report return-center behavior separately; no significance or accuracy claim.

Stop after seven valid planned captures. Permit at most one replacement per
capture for a documented non-angular failure (decode failure, missing features,
motion, glare/blur preventing a center decision, or a changed setting). Retain
failed attempts with `_attempt02` on replacements and record reasons. If the
replacement fails or the setup cannot remain controlled, pause and revise the
plan. Never add trials because an angle looks unfavorable or stop when a desired
error is reached. Do not inspect outcome angles until acquisition is complete.

Defer yaw/pitch/roll, distance/height, lens/zoom, stabilization and other modes
until a specific unresolved M9 baseline decision warrants another small test.
A right-angle target in one orientation can be insensitive to some projection
changes; a small difference here cannot establish general projection robustness.

## Remaining M4 closure evidence

Complete the acquisition/target records, run the feasible predeclared sequence,
report localization and recording variability separately, and document tested
camera conditions and limitations. Justify the provisional M9 setup and any
setup tolerances from adequate evidence; this screen alone need not justify all
tolerances. Keep optics/timing contributions explicitly unresolved where needed.
The existing M4 acceptance conditions and requirements remain unchanged.
