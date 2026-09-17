# I5 — Interactive Landmark Review

## Scope

I5 adds frame-local human review of MotionLab semantic landmarks without changing the frozen Core v0.1.0 evidence model.

The operator may drag a visible automatic landmark when its placement is visibly inappropriate for the intended semantic reference. Physical stickers or markers remain visual references for the human operator only; MotionLab does not automatically detect them in this milestone.

## Evidence model

Automatic landmark coordinates remain immutable. A manual correction is stored separately and becomes the effective point only while active:

```text
effective position = active manual correction if present
                     otherwise automatic position
```

The original automatic coordinates remain available in frame responses and are never overwritten by UI dragging.

## Coordinate transform

The review overlay is displayed over a `contain`/letterboxed preview. Pointer coordinates therefore cannot be converted with a simple full-element scale when the preview and source aspect ratios differ.

For source dimensions `(W, H)` and overlay rectangle `(w, h)`:

```text
scale = min(w / W, h / H)
rendered_w = W * scale
rendered_h = H * scale
offset_x = (w - rendered_w) / 2
offset_y = (h - rendered_h) / 2

x_source = (x_pointer - offset_x) / scale
y_source = (y_pointer - offset_y) / scale
```

Pointer positions outside the rendered image area are rejected. Persisted correction coordinates remain in original decoded pixel coordinates.

## Interaction

A visible landmark handle can be dragged for the current frame only.

- drag previews the changed point and dependent segments locally;
- pointer release commits one correction for one frame/role;
- `Esc` cancels an active unsaved drag;
- reset deactivates the current correction and restores the automatic point;
- frame navigation is disabled while a correction request is being saved;
- the UI explicitly labels Automatic, Corrected and Missing states.

No correction is propagated to adjacent frames and no interpolation is introduced.

## Measurement recalculation

The frame API already evaluates displayed measurements from effective landmarks, so reviewed values update immediately after a correction response.

I5 also introduces an additive `reviewed_measurement_results` cache for reviewed state. It is separate from `measurement_results`, which remains the automatic analysis record.

The intended dependency graph is:

```text
shoulder -> trunk inclination
hip      -> knee flexion, trunk inclination
knee     -> knee flexion, shank-foot angle
ankle    -> knee flexion, shank-foot angle
toe      -> shank-foot angle
```

Only definitions affected by the edited role should be refreshed. Reviewed rows carry an `input_revision` based on active correction identifiers so cached values remain traceable to effective landmark state.

## Undo and reset

Correction rows are historical evidence rather than mutable replacements. I5 review services support restoring the previous correction when undoing the latest active correction. Reset remains distinct: it returns the effective point to the automatic landmark.

The API wiring for undo/review-cache persistence must preserve transaction boundaries: correction/reset/undo plus affected reviewed measurements should commit together or roll back together.

## Interpretation boundary

Manual review can fix visually obvious landmark placement errors. It does not by itself establish improved metrological or clinical accuracy, and a physical sticker is not automatically treated as anatomical ground truth.

## Privacy

All real corrections, reviewed measurements and session databases remain under the ignored local `workspace/` boundary. Public tests use synthetic points only.
