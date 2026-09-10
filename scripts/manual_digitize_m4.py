import cv2
import json
import math
from pathlib import Path

IMAGE = Path("data/raw/m4/baseline_001_frame_000.png")
OUTPUT = Path("data/raw/m4/baseline_001_digitization_04.json")

image = cv2.imread(str(IMAGE))
if image is None:
    raise FileNotFoundError(IMAGE)

original_h, original_w = image.shape[:2]

max_width = 1600
scale = min(1.0, max_width / original_w)

display = cv2.resize(
    image,
    (int(original_w * scale), int(original_h * scale)),
)

labels = ["A", "B", "C"]
points = []

def click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(points) < 3:
        original_x = x / scale
        original_y = y / scale

        label = labels[len(points)]
        points.append((original_x, original_y))

        cv2.circle(display, (x, y), 6, (0, 0, 255), -1)
        cv2.putText(
            display,
            label,
            (x + 10, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
        )

        cv2.imshow("M4 digitization", display)

cv2.namedWindow("M4 digitization", cv2.WINDOW_NORMAL)
cv2.imshow("M4 digitization", display)
cv2.setMouseCallback("M4 digitization", click)

print("Click the CENTER of A, then B, then C.")

while len(points) < 3:
    if cv2.waitKey(20) & 0xFF == 27:
        raise SystemExit("Cancelled.")

cv2.destroyAllWindows()

A, B, C = points

def angle(a, b, c):
    u = (a[0] - b[0], a[1] - b[1])
    v = (c[0] - b[0], c[1] - b[1])

    dot = u[0] * v[0] + u[1] * v[1]
    nu = math.hypot(*u)
    nv = math.hypot(*v)

    cosine = max(-1.0, min(1.0, dot / (nu * nv)))
    return math.degrees(math.acos(cosine))

angle_deg = angle(A, B, C)

record = {
    "source_image": str(IMAGE),
    "image_width_px": original_w,
    "image_height_px": original_h,
    "click_order": ["A", "B", "C"],
    "points_px": {
        "A": {"x": A[0], "y": A[1]},
        "B": {"x": B[0], "y": B[1]},
        "C": {"x": C[0], "y": C[1]},
    },
    "angle_ABC_deg": angle_deg,
    "nominal_reference_deg": 90.0,
    "signed_difference_deg": angle_deg - 90.0,
}

OUTPUT.write_text(json.dumps(record, indent=2), encoding="utf-8")

print(json.dumps(record, indent=2))
print(f"\nSaved to: {OUTPUT}")
