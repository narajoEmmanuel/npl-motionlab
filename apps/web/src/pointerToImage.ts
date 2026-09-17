/** Convert viewport pointer coordinates through centered contain letterboxing. */
export function pointerToImage(
  rect: { left: number; top: number; width: number; height: number },
  video: { decoded_width_px: number; decoded_height_px: number },
  clientX: number,
  clientY: number,
): { x: number; y: number } | null {
  const scale = Math.min(rect.width / video.decoded_width_px, rect.height / video.decoded_height_px);
  if (!Number.isFinite(scale) || scale <= 0) return null;
  const renderedWidth = video.decoded_width_px * scale;
  const renderedHeight = video.decoded_height_px * scale;
  const localX = clientX - rect.left - (rect.width - renderedWidth) / 2;
  const localY = clientY - rect.top - (rect.height - renderedHeight) / 2;
  if (localX < 0 || localY < 0 || localX > renderedWidth || localY > renderedHeight) return null;
  return { x: Math.min(video.decoded_width_px, Math.max(0, localX / scale)),
           y: Math.min(video.decoded_height_px, Math.max(0, localY / scale)) };
}
