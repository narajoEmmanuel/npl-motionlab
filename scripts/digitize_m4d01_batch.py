"""Collect fresh human A/B/C picks without displaying angles or earlier picks."""
import argparse
import hashlib
import json
from pathlib import Path

import cv2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--operator', required=True, help='Private operator identifier')
    args = parser.parse_args()
    manifest = json.loads((args.directory / 'm4d01_manifest.json').read_text())
    for entry in manifest['captures']:
        cid = entry['capture_id']
        path = args.directory / f'{cid}_frame_000.png'
        frame = cv2.imread(str(path))
        if frame is None:
            raise ValueError('Missing frame')
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['frame_sha256']
        h, w = frame.shape[:2]
        scale = min(1.0, 1600 / w)
        base = cv2.resize(frame, (int(w * scale), int(h * scale)))
        for repeat in range(1, 5):
            output = args.directory / f'{cid}_digitization_{repeat:02d}.json'
            if output.exists():
                previous = json.loads(output.read_text())
                if previous.get('operator_id') != args.operator:
                    raise ValueError('Existing record belongs to another operator')
                continue
            points = []
            display = base.copy()
            window = f'{cid} repeat {repeat}: click A, B, C; Esc cancels'
            def click(event, x, y, flags, param):
                if event == cv2.EVENT_LBUTTONDOWN and len(points) < 3:
                    label = 'ABC'[len(points)]
                    points.append((x / scale, y / scale))
                    cv2.circle(display, (x, y), 6, (0, 0, 255), -1)
                    cv2.putText(display, label, (x+10, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    cv2.imshow(window, display)
            cv2.namedWindow(window, cv2.WINDOW_AUTOSIZE)
            cv2.imshow(window, display)
            cv2.setMouseCallback(window, click)
            while len(points) < 3:
                if cv2.waitKey(20) & 0xFF == 27:
                    cv2.destroyAllWindows()
                    return
            cv2.destroyAllWindows()
            record = dict(capture_id=cid, operator_id=args.operator,
                image_width_px=w, image_height_px=h, frame_sha256=entry['frame_sha256'],
                display_width_px=base.shape[1], scale=scale,
                procedure='Fresh A/B/C geometric-center clicks; no prior picks or angle results displayed',
                tool='digitize_m4d01_batch.py', opencv_version=cv2.__version__,
                click_order=list('ABC'), nominal_reference_deg=90.0,
                points_px={k:dict(x=p[0], y=p[1]) for k,p in zip('ABC', points)})
            with output.open('x', encoding='utf-8') as stream:
                json.dump(record, stream, indent=2)
            print(f'Saved {cid} repeat {repeat}; angles withheld.')
    print('All picks saved. Recalculate with motionlab.geometry before analysis.')


if __name__ == '__main__':
    main()
