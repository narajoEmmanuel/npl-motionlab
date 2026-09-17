import type { FrameSnapshot } from "./types";

export function linePoints(rows: FrameSnapshot[], key: string, width: number, height: number) {
  const values = rows
    .map((row) => row.measurements[key])
    .filter((value) => value?.valid && value.value_deg !== null)
    .map((value) => value!.value_deg as number);
  if (!values.length || rows.length < 2) return "";
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = Math.max(1e-9, max - min);
  let connected = false;
  return rows
    .map((row, index) => {
      const measurement = row.measurements[key];
      if (!measurement?.valid || measurement.value_deg === null) {
        connected = false;
        return null;
      }
      const x = (index / Math.max(1, rows.length - 1)) * width;
      const y = height - ((measurement.value_deg - min) / span) * height;
      const point = `${connected ? "L" : "M"}${x.toFixed(2)},${y.toFixed(2)}`;
      connected = true;
      return point;
    })
    .filter(Boolean)
    .join(" ");
}
