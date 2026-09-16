# Controlled Terminology

Use these terms consistently in code, documentation, analysis, and public
communication. The simplified Core adopted on 2026-09-16 does not require every
term below to appear in the final analysis. Reference-comparison, uncertainty,
and robustness terms are retained because they remain valid for optional or
future extensions.

| Term | MotionLab meaning | Avoid confusing it with |
|---|---|---|
| Measurand | Quantity intended to be measured: the 2D projected sagittal-plane knee flexion angle under specified conditions. | A pose-model output or anatomical 3D joint angle. |
| 2D projected knee flexion angle | Image-plane angle derived from projected thigh and shank geometry, using 0° for projected extension and increasing positive flexion. | Full anatomical knee kinematics. |
| Included segment angle | Generic geometric angle between projected knee-to-hip and knee-to-ankle vectors. | The project flexion convention; the two are supplementary. |
| Measurement model | Mathematical and procedural relationship connecting landmark coordinates and declared conditions to the reported angle. | Only the pose model or only the angle formula. |
| Core workflow | The bounded source-video → Sports2D landmarks → MotionLab geometry → repeated-trial result path defined in `docs/roadmap.md`. | Every possible future MotionLab extension. |
| External pose engine | Versioned third-party system used to localize landmarks. The selected Core workflow uses Sports2D/RTMPose. | The MotionLab measurement system itself. |
| Markerless estimate | Projected angle calculated from pose-estimator landmarks by MotionLab geometry. | Ground truth. |
| Trial | One independently recorded Core squat video under the fixed practical setup. | A frame or every sample in one video. |
| Observation | A frame-level or event-level value within a trial. | An independent replicate by default. |
| Repeated-trial variation | Descriptive variation among independent Core trial results under the fixed setup. | Full repeatability, reproducibility, or population variability unless those conditions are explicitly studied. |
| Failure | Predefined inability to produce a valid result or meet a stated quality rule. | An inconvenient result removed after analysis. |
| Engineering conclusion | Evidence-bounded interpretation of what the tested workflow demonstrated under the tested conditions. | Universal validation. |
| Reference measurement | Optional independently obtained comparison value, for example from a later Kinovea appendix. | Error-free truth. |
| Signed difference | MotionLab result minus an optional reference result, using the declared sign convention. | Uncertainty. |
| Absolute difference | Absolute value of the signed difference. | Bias. |
| Bias | Estimated systematic component of paired differences for a defined comparison design. | Any single-trial difference. |
| Agreement | Closeness between two measurement procedures assessed through their differences. | Correlation or association. |
| Accuracy | Closeness of agreement between a measured value and the quantity value being measured; use cautiously when no error-free reference exists. | Precision. |
| Precision | Closeness among repeated measured values under specified conditions. | Accuracy. |
| Repeatability | Precision under explicitly stated repeatability conditions. | The simple five-trial descriptive variation reported by the Core unless the required conditions are actually established. |
| Measurement uncertainty | Non-negative parameter characterizing dispersion of quantity values attributed to the measurand, based on stated information and assumptions. | Observed trial spread or a modeled pixel perturbation. |
| Robustness | Stability of performance under predefined controlled variations. | The fixed-condition Core experiment. |
| Exploratory simulation | Modeled sensitivity analysis using hypothetical or weakly informed inputs. | Experimentally quantified uncertainty. |
| Optional appendix | Work that may strengthen the portfolio or explore a secondary technical question but is not required to complete the Core. | A hidden blocking requirement. |

## Evidence labels

| Label | Meaning | Core role |
|---|---|---|
| V1 | Analytically verified | Core |
| V2 | Unit-tested | Core |
| V3 | Experimentally observed | Core |
| V4 | Reference-compared | Optional Kinovea appendix |
| V5 | Uncertainty-characterized | Future work |
| V6 | Robustness-tested | Future work |
| V7 | Literature-supported | Context only, never project validation by itself |

Claims must state or link to the evidence that supports them. Planned or
optional work is not evidence, and the absence of an optional evidence layer
does not prevent completion of the simplified Core.
