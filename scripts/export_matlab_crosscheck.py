"""Generate Python reference results for MATLAB cross-verification."""
from __future__ import annotations
import argparse, csv
from pathlib import Path
from motionlab.geometry import angle_from_points_deg
DEFAULT_CASES = Path("matlab/verification/crosscheck_cases.csv")
DEFAULT_OUTPUT = Path("matlab/results/python_crosscheck_results.csv")
def generate(cases_path: Path, output_path: Path) -> list[dict[str, str]]:
    with cases_path.open(newline="", encoding="utf-8") as stream:
        cases = list(csv.DictReader(stream))
    if not cases:
        raise ValueError("Cross-check case file is empty.")
    rows=[]
    for case in cases:
        proximal=(float(case["proximal_x"]),float(case["proximal_y"]))
        joint=(float(case["joint_x"]),float(case["joint_y"]))
        distal=(float(case["distal_x"]),float(case["distal_y"]))
        angle=angle_from_points_deg(proximal,joint,distal)
        expected_text=case.get("expected_angle_deg","").strip()
        expected=float(expected_text) if expected_text else None
        rows.append({"case_id":case["case_id"],"python_angle_deg":f"{angle:.17g}","expected_angle_deg":expected_text,"analytical_abs_error_deg":f"{abs(angle-expected):.17g}" if expected is not None else ""})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer=csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    return rows
def main()->int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--cases",type=Path,default=DEFAULT_CASES); parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); args=parser.parse_args(); rows=generate(args.cases,args.output); print(f"Wrote {len(rows)} Python cross-check cases to {args.output}"); return 0
if __name__=="__main__": raise SystemExit(main())
