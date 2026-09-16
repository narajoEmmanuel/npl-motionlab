# Deterministic landmark sensitivity analysis

## Engineering question

How much can the calculated 2D included angle change when one landmark is moved by a small, known image-plane displacement?

## Design

M4-E uses synthetic baseline geometries at 30°, 60°, 90°, 120°, and 150°, with 100-pixel proximal and distal segments. One landmark at a time is perturbed by 1, 2, 3, and 5 pixels per axis. Modes are x-only with both signs, y-only with both signs, and equal x/y displacement with all four sign combinations. The equal x/y mode has Euclidean displacement `sqrt(2)*magnitude` and is reported explicitly.

The workflow retains every simulated case, grouped mean and maximum absolute angular differences, plus a linear fit over the 1, 2, and 3 pixel levels. Figures compare landmarks, horizontal versus vertical sensitivity, and dependence on baseline geometry.

## Interpretation

These are modeled simulation results, not measured landmark-localization errors. No probability distribution is assigned. Therefore M4-E does not complete M13 uncertainty or M14 empirically informed Monte Carlo. It provides exploratory sensitivity evidence that may inform those later milestones.
