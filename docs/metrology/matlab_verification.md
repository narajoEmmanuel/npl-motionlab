# MATLAB analytical verification

`matlab/geometry/compute_angle_2d.m` independently implements the same unsigned included 2D angle as the verified Python geometry, using normalized vectors and `atan2d(abs(det), dot)`.

`verify_known_angles.m` constructs synthetic cases directly from known geometry at 0°, 30°, 45°, 60°, 90°, 120°, 150°, and 180°. Expected values do not come from Python. The numerical tolerance is `1e-10°`, which is a software-verification tolerance, not an experimental acceptance criterion.

The source and reproducible workflow are implemented. A MATLAB analytical-verification result must not be claimed until the workflow is executed in an identified MATLAB release and the generated table is reviewed. This layer verifies mathematics and implementation only, not camera behavior, landmarks, biomechanics, or clinical accuracy.
