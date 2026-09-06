# Controlled Terminology

Use these terms consistently in code, documentation, analysis, and public
communication. Definitions may be refined when supported by later metrology and
literature work, but changes must preserve traceability.

| Term | MotionLab meaning | Avoid confusing it with |
|---|---|---|
| Measurand | Quantity intended to be measured: the 2D projected sagittal-plane knee flexion angle under specified conditions. | A pose model output or an anatomical 3D joint angle. |
| 2D projected knee flexion angle | Image-plane angle derived from projected thigh and shank segment geometry, using 0° for projected extension and increasing positive flexion. | Full anatomical knee kinematics. |
| Included segment angle | Geometric angle between the projected knee-to-hip and knee-to-ankle vectors. | The flexion convention; the two are supplementary under the working definition. |
| Measurement model | Mathematical and procedural relationship connecting image coordinates and influence quantities to the reported angle. | Only the angle formula. |
| Measurement system | Camera, acquisition protocol, participant/task conditions, software, pose model, processing, reference method, operators, and traceability records considered together. | MediaPipe, OpenPose, MoveNet, or any single component. |
| Markerless estimate | Projected angle calculated from pose-estimator landmarks without using visible reference markers for localization. | Ground truth. |
| Reference measurement | Independently obtained comparison value from the qualified same-video reference procedure. | An error-free true value. |
| Error | Markerless estimate minus reference measurement, using the declared sign convention. | Uncertainty or absolute error. |
| Signed error | Direction-preserving difference between markerless and reference values. | Error magnitude. |
| Absolute error | Absolute value of signed error. | Bias. |
| Bias | Estimated systematic component of measurement differences for a defined condition and analysis unit. | Any single-trial error. |
| Agreement | Closeness between markerless and reference measurements assessed through differences and their distribution. | Correlation or association. |
| Accuracy | Closeness of agreement between a measured value and the quantity value being measured; used cautiously because the accessible reference is imperfect. | Precision. |
| Precision | Closeness among repeated measured values under specified conditions. | Accuracy or correctness. |
| Repeatability | Precision under specified repeatability conditions, including what remains unchanged and the repetition interval. | Agreement with the reference. |
| Reproducibility | Precision under specified changed conditions, or the ability to recreate computational results; the intended meaning must be stated. | Repeatability. |
| Measurement uncertainty | Non-negative parameter characterizing dispersion of quantity values attributed to the measurand, based on stated information and assumptions. | Observed error or standard deviation alone. |
| Experimental unit | Smallest independently assigned or repeated entity supporting the question, likely a trial or higher-level unit depending on design. | A video frame by default. |
| Observation | Recorded value at a frame, event, or other sampling point. | An independent replicate. |
| Pilot data | Data used to evaluate feasibility and refine procedures before freezes. | Confirmatory evidence. |
| Confirmatory data | Data collected and analyzed under the frozen protocol, SAP, exclusions, and criterion. | Pilot data reused after inspection. |
| Failure | Predefined inability to produce a valid measurement or meet a quality rule. | An inconvenient result removed after analysis. |
| Robustness | Stability of measurement performance under predefined, controlled variations relevant to intended use. | Uncontrolled heterogeneity. |
| Exploratory simulation | Modeled sensitivity analysis using explicitly hypothetical or weakly informed inputs. | Experimentally quantified uncertainty. |
| Engineering decision | Evidence-based classification of suitability for the bounded intended use under stated conditions. | Universal validity. |

## Evidence labels

| Label | Meaning |
|---|---|
| V1 | Analytically verified |
| V2 | Unit-tested |
| V3 | Experimentally observed |
| V4 | Reference-compared |
| V5 | Uncertainty-characterized |
| V6 | Robustness-tested |
| V7 | Literature-supported |

Claims must state or link to the evidence that supports them. Planned work is
not evidence, and absence of evidence must not be rewritten as validation.
