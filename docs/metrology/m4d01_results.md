# M4-D horizontal image-position results

## Scope and verification

This report completes the predefined seven-recording M4-D image-position
analysis. It compares three horizontally centered recordings, three
right-position recordings, and one return-to-center diagnostic. Each retained
first frame was digitized four times by `operator_01` using the same 1600-pixel
display width, A/B/C order, geometric-center rule, and hidden-result procedure.

The 28 private records intentionally contain coordinates rather than saved
angle results. Every angle below was independently calculated from the saved
A/B/C pixel coordinates using the verified
`motionlab.geometry.angle_from_points_deg` implementation. Frame checksums,
operator, procedure, display scale, image dimensions, click order, and nominal
reference were validated before analysis. The private analysis record retains
all 28 calculated values and the nested summaries.

The unit for the Center-versus-Right comparison is the recording mean. The four
digitizations within a frame characterize exploratory manual localization
sensitivity and are not independent camera trials.

## Per-capture results

| Capture | Mean ABC (°) | Mean signed difference (°) | Within-frame sample SD (°) | Range (°) | Mean absolute difference (°) | Mean B (px) | Mean B (x/W, y/H) |
|---|---:|---:|---:|---:|---:|---:|---:|
| m4d01_C_01 | 90.310557 | +0.310557 | 0.705296 | 1.556480 | 0.676921 | (961.8, 668.7) | (0.50094, 0.61917) |
| m4d01_C_02 | 90.555849 | +0.555849 | 0.483745 | 1.145762 | 0.594603 | (962.4, 668.7) | (0.50125, 0.61917) |
| m4d01_C_03 | 90.248571 | +0.248571 | 0.203397 | 0.498212 | 0.248571 | (961.5, 668.4) | (0.50078, 0.61889) |
| m4d01_R_01 | 91.448604 | +1.448604 | 0.495739 | 0.949567 | 1.448604 | (1303.5, 667.5) | (0.67891, 0.61806) |
| m4d01_R_02 | 91.384901 | +1.384901 | 0.443294 | 0.966561 | 1.384901 | (1303.8, 667.5) | (0.67906, 0.61806) |
| m4d01_R_03 | 91.607057 | +1.607057 | 0.258110 | 0.626316 | 1.607057 | (1304.1, 666.6) | (0.67922, 0.61722) |
| m4d01_C_return_01 | 90.202706 | +0.202706 | 0.681306 | 1.624505 | 0.446128 | (997.5, 669.9) | (0.51953, 0.62028) |

The `C` and `R` labels describe the intended conditions. Achieved B positions
show that Center was horizontally centered near 0.501W, while Right reached
about 0.679W rather than the planned 0.75W. Both were below vertical center at
about 0.618–0.619H. The return reached 0.520W, so it was not an exact return to
the initial horizontal position. The achieved Right-minus-Center mean shift of
B was +341.9 px horizontally (+0.17807W) and -1.4 px vertically (-0.00130H).

## Condition and return summaries

| Quantity | Center | Right |
|---|---:|---:|
| Recording means (°) | 90.310557, 90.555849, 90.248571 | 91.448604, 91.384901, 91.607057 |
| Mean of three recording means (°) | 90.371659 | 91.480187 |
| Mean signed difference from nominal (°) | +0.371659 | +1.480187 |
| Between-recording sample SD of means (°) | 0.162496 | 0.114396 |
| Range of recording means (°) | 0.307277 | 0.222156 |
| Mean within-frame sample SD (°) | 0.464146 | 0.399048 |
| Achieved mean B (px) | (961.9, 668.6) | (1303.8, 667.2) |
| Achieved mean B (x/W, y/H) | (0.50099, 0.61907) | (0.67906, 0.61778) |

The observed Right-minus-Center difference between condition means is
**+1.108528°**. This is a descriptive difference for the tested acquisition
sequence and achieved positions. No significance test or final acceptance
threshold is applied.

The return-to-center mean is **90.202706°**, with signed difference +0.202706°,
within-frame sample SD 0.681306°, range 1.624505°, and mean absolute difference
0.446128°. It is 0.168953° below the initial Center condition mean. Because its
B position was about 35.6 pixels farther right than the initial Center mean and
only one return recording exists, it is a drift/return diagnostic rather than
an independent estimate of return reproducibility.

#### Variability at different levels

Within-frame manual variability is represented by each capture's four-click
sample SD and range. The pooled within-frame sample SD, formed from residuals
around each of the seven frame means with 21 residual degrees of freedom, is
**0.499412°**. This does not include between-frame or physical effects.

Between-recording variability uses the three recording means per main
condition: sample SD 0.162496° for Center and 0.114396° for Right. These values
describe start/stop recordings made without independent camera or target setup
reinstallation. They do not measure between-session or setup repeatability.
The 28 digitizations are never pooled as 28 independent camera observations.

## Interpretation and provisional choice

All three Right recording means exceed every Center recording mean, and the
Right condition mean is 1.108528° higher at the achieved positions. The small
between-recording spread relative to this descriptive difference makes the
direction consistent within this sequence. Manual digitization variability is
visible and sometimes larger within a single frame than between recording
means, but averaging four predefined digitizations produces separated Center
and Right recording means in these data.

This evidence supports a **provisional M9 preference for horizontal centering**
of the target/measurand under this tested setup. It does not establish a
general lens-distortion map, performance at 0.75W or image edges, vertical
field-position behavior, or robustness to camera pose and distance. The
preference also does not establish camera accuracy: differences from nominal
combine target construction, ruler measurement, camera projection, optics,
decoding, and manual localization. Physical target uncertainty remains
unquantified. The reported 30 FPS remains header metadata rather than evidence
of constant frame timing.

## M4 status and next action

M4 is not complete. This experiment supplies physical-image evidence for one
factor and supports a provisional horizontal-position choice, but it does not
justify numerical setup tolerances. Requested capture resolution/FPS and
HDR/stabilization/focus/exposure/white-balance behavior remain unknown. The
separate asymmetric mark was not positively identified in the reviewed frames,
although labels and the board clip supplied orientation cues. The private
target companion record and a corrected baseline acquisition record remain
outstanding.

Next, consolidate the private target/acquisition records and state the
provisional M9 camera configuration with centered horizontal framing. Then
identify which setup tolerance is necessary for reproducibly implementing that
baseline and design only the smallest supporting M4 test. Do not add a new
condition until that decision is documented. M5 must not begin until the M4
acceptance conditions are satisfied or a documented scope decision defers a
specific limitation.
