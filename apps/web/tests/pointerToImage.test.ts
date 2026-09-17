import test from "node:test";
import assert from "node:assert/strict";
import { pointerToImage } from "../src/pointerToImage.ts";

const video = { decoded_width_px: 640, decoded_height_px: 480 };
for (const [name, width, height, offsetX, offsetY] of [
  ["same aspect", 320, 240, 0, 0],
  ["wider container", 800, 480, 80, 0],
  ["taller container", 640, 800, 0, 160],
] as const) {
  test(name + ": original pixels, corners and outside", () => {
    const rect = { left: 25, top: 40, width, height };
    const scale = Math.min(width / 640, height / 480);
    const x = rect.left + offsetX, y = rect.top + offsetY;
    assert.deepEqual(pointerToImage(rect, video, x, y), { x: 0, y: 0 });
    assert.deepEqual(pointerToImage(rect, video, x + 640 * scale, y + 480 * scale), { x: 640, y: 480 });
    assert.deepEqual(pointerToImage(rect, video, x + 137 * scale, y + 219 * scale), { x: 137, y: 219 });
    assert.equal(pointerToImage(rect, video, x - 1, y), null);
    assert.equal(pointerToImage(rect, video, x, y - 1), null);
    assert.equal(pointerToImage(rect, video, x + 640 * scale + 1, y), null);
    assert.equal(pointerToImage(rect, video, x, y + 480 * scale + 1), null);
  });
}
test("zero size cannot persist a correction", () => {
  assert.equal(pointerToImage({ left: 0, top: 0, width: 0, height: 0 }, video, 0, 0), null);
});
