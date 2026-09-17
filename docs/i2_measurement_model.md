# I2 — Interactive Measurement Model

## Scope

I2 introduces the versioned semantic measurement layer used by MotionLab Interactive.
It does not change the released Core v0.1.0 knee measurement or claims.

The measurement layer works with MotionLab semantic landmarks rather than UI
coordinates or raw external-engine column names.

Initial semantic roles:

```text
shoulder
hip
knee
ankle
toe
```

## Verified pinned-engine mapping

On 2026-09-17, the marker header of a retained private M7 pixel TRC was inspected
directly, without reading its coordinate rows. Its adjacent engine provenance
confirms Sports2D **0.8.34**, Pose2Sim **0.10.49**, model **Body_with_feet**.
Only external marker names are published here; human coordinates are not fixtures.

| MotionLab semantic role | Right external marker | Left external marker |
|---|---|---|
| shoulder | `RShoulder` | `LShoulder` |
| hip | `RHip` | `LHip` |
| knee | `RKnee` | `LKnee` |
| ankle | `RAnkle` | `LAnkle` |
| toe | `RBigToe` | `LBigToe` |

All foot candidates present in that header are `RBigToe`, `RSmallToe`, `RHeel`,
`LBigToe`, `LSmallToe`, and `LHeel`.

The first shank-foot definition selects **BigToe**, a named anterior toe endpoint,
to define a reproducible Ankle->Toe ray. SmallToe is another anterior candidate;
the header alone does not establish which point is more accurate. Heel is a
posterior endpoint. This choice specifies geometry, not clinical dorsiflexion or
an anatomical foot-axis validation. No averaging or fallback to other foot markers
is performed. Changing the toe endpoint later requires an explicit definition/
mapping decision because it changes the measured ray.

`SPORTS2D_BODY_WITH_FEET_INTERACTIVE_LANDMARKS` contains the five-role mapping.
`semantic_landmarks_from_sports2d` maps external pixel columns into semantic
columns, preserving frame order, engine time, pixel values and missing coordinates.
Absent required columns raise an explicit error; row-level NaN coordinates remain
NaN so the registry reports `missing_landmark`.

The existing `SPORTS2D_BODY_WITH_FEET_LANDMARKS` deliberately retains only hip,
knee and ankle. The frozen knee pipeline serializes that mapping in provenance,
and retained Core readers require the original three-role contract. Keeping the
interactive mapping separate preserves Core output columns, calculations and
provenance compatibility. Knee-only TRCs do not need shoulder or toe columns.

Adding the interactive adapter changes the module's byte hash. Historical Core
provenance is not rewritten, and its strict frozen-module validator is not relaxed.
Reproduce frozen M7/M8 evidence at its recorded Core revision; the I2 checkout
preserves knee behavior but is not byte-identical to that historical adapter.

## Versioned definitions

Three definitions are registered:

| Name | Display name | Version | Dependencies |
|---|---|---:|---|
| `projected_knee_flexion` | 2D projected knee flexion | 1 | hip, knee, ankle |
| `projected_shank_foot_angle` | 2D projected shank-foot angle | 1 | knee, ankle, toe |
| `projected_trunk_inclination` | 2D projected trunk inclination | 1 | hip, shoulder |

All outputs are degrees.

## Knee flexion

I2 reuses the same verified generic geometry as the Core:

```text
included = angle(Hip, Knee, Ankle)
projected knee flexion = 180 deg - included
```

No alternate knee formula is introduced.

## Shank-foot angle

The geometric definition is:

```text
Knee -> Ankle -> Toe
```

with Ankle as the vertex. The result is the unsigned included image-plane angle
in `[0, 180]` degrees.

The result is intentionally named **2D projected shank-foot angle**. It is not
called dorsiflexion or plantarflexion because no clinical zero/reference
convention has been established.

## Trunk inclination

The trunk segment is:

```text
Hip -> Shoulder
```

The reference direction is image vertical upward:

```text
(0, -1)
```

because image coordinates increase downward in `y`.

The vertical ray conceptually starts at Hip, so both compared vectors share the
Hip origin. The unsigned angle is `0 deg` when Hip->Shoulder is vertical upward,
`90 deg` when horizontal and `180 deg` when pointing downward.

This is **2D projected trunk inclination**, not a spine-angle or spinal-curvature
measurement. If the camera is rolled, image vertical is not necessarily physical
vertical.

## Validity

A measurement is valid only when all required semantic landmarks are present,
finite and non-degenerate.

I2 preserves the established MotionLab validity vocabulary:

```text
missing_landmark
degenerate_geometry
```

No interpolation or synthetic landmark replacement occurs in this layer.

## Dependency-aware recalculation

The registry exposes which measurements depend on one edited landmark:

```text
shoulder -> trunk inclination
hip      -> knee flexion, trunk inclination
knee     -> knee flexion, shank-foot angle
ankle    -> knee flexion, shank-foot angle
toe      -> shank-foot angle
```

This is the dependency contract later used by the review/application service so
a frame-local manual edit does not require unrelated measurement recalculation.

## I2 boundary

Implemented in I2:

- pure knee/shank-foot/trunk geometry;
- explicit versioned measurement registry;
- dependency metadata;
- explicit validity evaluation;
- synthetic verification.

Local verification completed:

- exact right/left shoulder and toe/forefoot names read from the retained header;
- explicit BigToe endpoint choice with all foot candidates recorded above;
- synthetic adapter tests for both sides, unchanged Core mapping, original pixels,
  frame order, missing columns and missing coordinates.

Not part of I2:

- FastAPI;
- UI;
- video playback;
- manual drag behavior;
- automatic physical-marker detection;
- clinical interpretation;
- 3D measurements.
