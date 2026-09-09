"""Register seven explicitly ordered M4-D originals; never calculate angles."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

import cv2
import numpy as np
import yaml

from motionlab.video_metadata import inspect_video


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    ids = ['m4d01_C_01', 'm4d01_C_02', 'm4d01_C_03',
           'm4d01_R_01', 'm4d01_R_02', 'm4d01_R_03', 'm4d01_C_return_01']
    times = ['22:40:23', '22:40:29', '22:40:34', '22:41:03',
             '22:41:10', '22:41:18', '22:41:39']
    names = [f'IMG_{i}.MOV' for i in range(4870, 4877)]
    destination = args.destination
    template = yaml.safe_load(Path('docs/metrology/acquisition_record_template.yaml').read_text())
    targets = [destination / 'm4d01_manifest.json']
    for name, cid in zip(names, ids):
        if not (args.source / name).is_file():
            raise FileNotFoundError(name)
        targets.extend([destination / name, destination / f'{cid}_metadata.json',
                        destination / f'{cid}_frame_000.png',
                        destination / f'{cid}_acquisition.yaml'])
    if any(p.exists() for p in targets):
        raise FileExistsError('Registration output already exists; nothing overwritten.')
    destination.mkdir(parents=True, exist_ok=True)
    entries = []
    for name, cid, encoded_time in zip(names, ids, times):
        source = args.source / name
        raw = destination / name
        before = digest(source)
        shutil.copy2(source, raw)
        assert digest(raw) == before == digest(source)
        metadata = inspect_video(raw).to_dict()
        assert metadata['sha256'] == before
        (destination / f'{cid}_metadata.json').write_text(
            json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
        cap = cv2.VideoCapture(str(raw))
        try:
            auto = cap.get(cv2.CAP_PROP_ORIENTATION_AUTO)
            ok, frame = cap.read()
            if not ok or frame is None:
                raise ValueError(f'First frame failed: {cid}')
        finally:
            cap.release()
        png = destination / f'{cid}_frame_000.png'
        if not cv2.imwrite(str(png), frame):
            raise IOError('PNG write failed')
        assert np.array_equal(frame, cv2.imread(str(png)))
        record = yaml.safe_load(yaml.safe_dump(template))
        record['condition_id'] = cid
        record['device'].update(manufacturer='Apple', model='iPhone 17 Pro Max')
        record['requested_capture'].update(orientation='landscape',
                                           lens='rear main', digital_zoom=1.0)
        record['physical_setup'].update(support='tripod', camera_height_mm=200,
            camera_to_target_distance_mm=1000, target_id='target_345_half_v1',
            target_record_path='target_345_half_v1.yaml',
            lighting_description='User reports held constant')
        record['observed_file_metadata'] = f'{cid}_metadata.json'
        record['notes'] = ('Setup reported retrospectively by user: height and distance approximate; '
            'phone fixed; target flat whiteboard in same plane/depth. BA=150, BC=200, AC=250 mm '
            'measured center-to-center with ruler; physical uncertainty unquantified. '
            '1x reported; requested resolution/FPS and HDR/stabilization/focus/exposure/white balance '
            'unknown, preserved as null. Original downloaded from iCloud. '
            'Capture order supplied by user, corroborated by embedded encoding time; '
            'encoding time is not asserted to be shutter/capture time. '
            'Actual field placement and quality recorded separately; no inferred yaw/pitch/roll.')
        (destination / f'{cid}_acquisition.yaml').write_text(
            yaml.safe_dump(record, sort_keys=False), encoding='utf-8')
        entries.append(dict(capture_id=cid, original_filename=name, sha256=before,
            source_path=str(source), source_size_bytes=source.stat().st_size,
            source_mtime_ns=source.stat().st_mtime_ns,
            windows_media_date_encoded=f'2026-09-09 {encoded_time}',
            timestamp_note='Shell System.Media.DateEncoded as displayed; timezone unconfirmed',
            mapping_basis='User order plus strictly increasing embedded encoding times; visual check pending',
            first_frame_index=0, frame_sha256=digest(png), opencv_version=cv2.__version__,
            orientation_auto=auto, quality_status='pending visual review',
            digitization_status='pending original operator; no angle outcomes calculated'))
        print(cid, name, metadata['decoded_width_px'], metadata['decoded_height_px'],
              metadata['codec_fourcc'], metadata['frame_count_reported'],
              metadata['nominal_fps_reported'], metadata['backend_orientation_degrees'])
    (destination / 'm4d01_manifest.json').write_text(
        json.dumps(dict(captures=entries), indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
