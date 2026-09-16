# Python-MATLAB numerical cross-verification

Cross-verification asks whether two independent implementations of the same mathematical model produce numerically consistent results for exactly the same coordinates. It does not test whether those coordinates are anatomically correct or whether the camera system is accurate.

`matlab/verification/crosscheck_cases.csv` is the neutral input. Python reads it with `scripts/export_matlab_crosscheck.py`, MATLAB recalculates the same cases independently, and the comparison report records Python angle, MATLAB angle, absolute numerical difference, and pass/fail against `1e-10°`.

A passing report supports only implementation consistency for the documented inputs and tolerance. It does not support markerless accuracy, camera accuracy, biomechanical validity, clinical validity, participant validation, or equivalence to 3D motion capture.
