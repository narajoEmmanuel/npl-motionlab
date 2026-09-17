import test from "node:test";
import assert from "node:assert/strict";
import { linePoints } from "../src/resultsChart.ts";
import type { FrameSnapshot } from "../src/types.ts";

function rows(values: (number | null)[]): FrameSnapshot[] {
  return values.map((value, frame_index) => ({
    frame_index, time_s: frame_index / 30, landmarks: {},
    measurements: { knee: { value_deg: value, valid: value !== null } },
  })) as unknown as FrameSnapshot[];
}

test("invalid frames split curves rather than imply interpolated values", () => {
  assert.equal(linePoints(rows([0, 10, null, 20, 30]), "knee", 400, 90),
    "M0.00,90.00 L100.00,60.00 M300.00,30.00 L400.00,0.00");
});

test("all-invalid curves are empty and flat curves remain finite", () => {
  assert.equal(linePoints(rows([null, null]), "knee", 100, 50), "");
  assert.equal(linePoints(rows([10, 10]), "knee", 100, 50), "M0.00,50.00 L100.00,50.00");
});
