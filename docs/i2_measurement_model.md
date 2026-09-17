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

The exact pinned Sports2D `Body_with_feet` column names for `shoulder` and `toe`
must be verified against the installed/local output before the adapter mapping is
extended. I2 must not guess those external names.

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

Still pending local verification before I2 can close:

- exact right/left shoulder external marker names in pinned Sports2D output;
- exact right/left toe/forefoot external marker names in pinned Sports2D output;
- adapter mapping tests using those verified names.

Not part of I2:

- FastAPI;
- UI;
- video playback;
- manual drag behavior;
- automatic physical-marker detection;
- clinical interpretation;
- 3D measurements.
