# M4-D seven-capture registration

All seven originals were copied without renaming into private Git-ignored raw
storage. Source hashes before/after copying, copy hashes and inspector hashes
matched. First-frame PNGs were checked pixel-for-pixel after lossless encoding.
Private manifest, seven metadata JSONs, seven acquisition YAMLs and a visual
quality review retain provenance. The subsequent predefined analysis is
reported in [M4-D horizontal image-position results](m4d01_results.md).

The embedded Windows `System.Media.DateEncoded` timestamps increase in the
supplied recording order. Filesystem download times do not resolve that order.
Embedded timezone is unconfirmed and encoding time is not asserted to be exact
capture time. First-frame board placement corroborates C/C/C/R/R/R/return.

| Capture | Original | Embedded time as displayed | Reported frames |
|---|---|---|---:|
| m4d01_C_01 | IMG_4870.MOV | 22:40:23 | 143 |
| m4d01_C_02 | IMG_4871.MOV | 22:40:29 | 141 |
| m4d01_C_03 | IMG_4872.MOV | 22:40:34 | 143 |
| m4d01_R_01 | IMG_4873.MOV | 22:41:03 | 138 |
| m4d01_R_02 | IMG_4874.MOV | 22:41:10 | 155 |
| m4d01_R_03 | IMG_4875.MOV | 22:41:18 | 141 |
| m4d01_C_return_01 | IMG_4876.MOV | 22:41:39 | 129 |

All decode as 1920 × 1080, HEVC, FFMPEG backend, nominal reported FPS 30,
orientation metadata 0. These are observed file properties, not requested
settings or evidence of CFR. The resolution differs from baseline_001.
Use this sequence's own center recordings for comparison.

User reports main rear camera, 1x, landscape, tripod, approximately 1000 mm
distance and 200 mm height; fixed phone, constant lighting and unchanged target
plane/depth. Requested resolution/FPS, HDR, stabilization, focus/exposure/white
balance remain null. The target is a flat whiteboard with ruler-measured
150/200/250 mm center distances, nominal 90 degrees, uncertainty unquantified.

All first frames show A/B/C and the complete board outline. Exposure is dark,
but centers remain distinguishable with no obvious obscuring glare or gross
blur. First-frame inspection does not certify whole-video motion stability.
A separate asymmetric mark cannot be positively identified; readable letters
and the side clip are visible orientation cues. Obtain operator identification
of the intended mark before claiming full protocol conformity.

B is below the planned vertical midpoint and the right placement is short of
the proposed 0.75W aim point. Return placement differs slightly from initial
center. Record achieved positions after digitization; do not relabel them as
the nominal levels. No capture was replaced or excluded based on angle.

## Manual observations and analysis

Four fresh digitizations per frame were completed by the same human operator;
the agent did not generate surrogate clicks. The batch picker preserves the
existing user script, maps a fixed 1600-pixel-wide display to original pixels,
starts each repeat from a clean frame, and withholds all angle results. Its
fixed window avoids interactive resizing; disclose this procedural clarification
if the baseline picker window was manually resized. It remains an uncharacterized
manual tool. Use the same operator, screen and geometric-center definition.

Run from the repository with a private operator ID:

```powershell
.\.venv\Scripts\python.exe scripts/digitize_m4d01_batch.py data/raw/m4 --operator OPERATOR_ID
```

It saved 28 separate coordinate records without overwriting prior records.
Every angle was then calculated from those coordinates with
`motionlab.geometry.angle_from_points_deg`. The public results keep within-frame
SD and between-recording SD separate. No significance testing, final threshold,
accuracy, camera bias or total uncertainty claim is made.

M4 remains incomplete. The bounded comparison supports a provisional M9
preference for horizontal centering with placement/configuration limitations
disclosed. Target uncertainty, camera/projection effects, timing, and
evidence-based setup tolerances remain unresolved. Keep original raw records
private and preserve earlier M4 evidence.
