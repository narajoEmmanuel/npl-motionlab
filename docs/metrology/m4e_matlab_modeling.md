# M4-E, MATLAB Measurement Modeling and Cross-Verification

## Status

**In progress.** Source implementation and documentation are present. MATLAB runtime execution, retained generated outputs, and private M4-D MATLAB replay remain required before declaring M4-E complete.

## Roadmap placement

M4-E is a submilestone inside M4, Camera & Image Verification. It strengthens the analytical and image-measurement foundations without renumbering the main roadmap or starting M5. Its deterministic perturbation tooling may later support M14, but it is not M14 completion because the inputs are modeled scenarios rather than empirically justified uncertainty distributions.

## Deliverables

Implemented source includes independent MATLAB 2D angle geometry, known-angle verification, normalized-to-pixel conversion, deterministic measurement modeling, landmark perturbation simulations, quantitative sensitivity analysis and figures, M4-D descriptive replay, neutral Python-MATLAB cross-check cases, and reproducibility documentation.

No MATLAB toolbox is required by design. Python dependencies are unchanged. Private M4-D data remain external to the public repository.

## Acceptance state

| Criterion | State |
|---|---|
| MATLAB source matches current angle definition | Implemented, runtime verification pending |
| Known synthetic cases | Implemented, MATLAB execution pending |
| Mathematical measurement model | Documented |
| Deterministic perturbation simulation | Implemented, MATLAB execution pending |
| Quantitative sensitivity outputs | Implemented, MATLAB execution pending |
| Existing M4-D replay | Implemented, private replay pending |
| Python-MATLAB comparison mechanism | Implemented, MATLAB comparison pending |
| Cross-language tolerance demonstrated | Pending MATLAB execution |
| Python regression suite | Must remain passing |
| Raw data modification | None intended |

## Claim discipline

After execution and review, M4-E can support claims about a mathematical measurement model, MATLAB implementation, deterministic landmark sensitivity, MATLAB replay of existing M4-D data, and cross-language implementation consistency. It does not support markerless biomechanical accuracy, pose-estimation accuracy, participant validation, completed measurement uncertainty, completed robustness validation, Vicon or 3D motion-capture equivalence, clinical application, or accreditation claims.
