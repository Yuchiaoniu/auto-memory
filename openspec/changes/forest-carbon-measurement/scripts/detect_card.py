#!/usr/bin/env python3
"""
OpenCV credit-card detection for Path A frame filtering.

Image mode:  positional JPEG paths (optionally --rotate-cw before paths)
Video mode:  --video <path> [--fps 2] [--save-dir <dir>] [--rotate-cw]

Output: JSON array, one object per frame
  {path, frameIdx, timeSec, cardDetected, isOrthogonal, angleDev,
   areaFrac, aspectRatio, sharpness, rotationAngle}

In video mode frames are saved to --save-dir (default: temp dir).
Card frames are rotated to horizontal before saving.
"""
import sys
import json
import math
import os
import glob
import subprocess
import tempfile
import numpy as np

try:
    import cv2
except ImportError:
    print(json.dumps({"error": "opencv not installed", "fix": "pip3 install opencv-python-headless"}), flush=True)
    sys.exit(1)

ASPECT_MIN = 1.4
ASPECT_MAX = 1.8
MIN_AREA_FRAC = 0.004
MAX_AREA_FRAC = 0.50
ORTHOGONAL_MAX_DEV = 20  # degrees

def _angle_deviation(pts):
    devs = []
    for i in range(4):
        v1 = pts[(i - 1) % 4] - pts[i]
        v2 = pts[(i + 1) % 4] - pts[i]
        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)
        if n1 < 1e-9 or n2 < 1e-9:
            continue
        cos_a = float(np.dot(v1, v2) / (n1 * n2))
        cos_a = max(-1.0, min(1.0, cos_a))
        devs.append(abs(math.degrees(math.acos(cos_a)) - 90.0))
    return max(devs) if devs else 90.0

def _laplacian(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())

def _card_rotation_angle(contour):
    """Angle (degrees) to rotate image so the card's long axis is horizontal."""
    rect = cv2.minAreaRect(contour)
    w, h = rect[1]
    angle = rect[2]  # [-90, 0)
    if w < h:
        angle += 90
    return angle

def _rotate_to_horizontal(img, contour):
    """Rotate image to align detected card's long axis with horizontal axis."""
    angle = _card_rotation_angle(contour)
    if abs(angle) < 0.5:
        return img, 0.0
    ih, iw = img.shape[:2]
    M = cv2.getRotationMatrix2D((iw // 2, ih // 2), angle, 1.0)
    rotated = cv2.warpAffine(img, M, (iw, ih),
                             flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_REPLICATE)
    return rotated, round(angle, 1)

MAX_DETECT_WIDTH = 960  # resize before detection to keep per-frame cost low
EARLY_EXIT_GOOD_FRAMES = 5  # break scan_video loop after this many orthogonal card hits

def detect_card(img):
    """Detect credit card in image. Returns (result_dict, best_contour)."""
    h, w = img.shape[:2]
    area_total = w * h
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    best = None
    best_contour = None
    for lo, hi in [(30, 100), (50, 150), (10, 60)]:
        edges = cv2.Canny(blur, lo, hi)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.dilate(edges, kernel, iterations=1)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            area = cv2.contourArea(c)
            area_frac = area / area_total
            if area_frac < MIN_AREA_FRAC or area_frac > MAX_AREA_FRAC:
                continue
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.03 * peri, True)
            if len(approx) != 4:
                # Tape measure may occlude one corner; retry on convex hull
                hull = cv2.convexHull(c)
                hull_peri = cv2.arcLength(hull, True)
                approx = cv2.approxPolyDP(hull, 0.03 * hull_peri, True)
                if len(approx) < 4 or len(approx) > 6:
                    continue
            rect = cv2.minAreaRect(c)
            rw, rh = sorted(rect[1])
            if rw < 1:
                continue
            ratio = rh / rw
            if not (ASPECT_MIN <= ratio <= ASPECT_MAX):
                continue
            if len(approx) == 4:
                pts = approx.reshape(4, 2).astype(float)
                ang_dev = _angle_deviation(pts)
            else:
                # Partial contour: derive angle from minAreaRect
                rw2, rh2 = rect[1]
                angle = rect[2]
                if rw2 < rh2:
                    angle += 90
                ang_dev = min(abs(angle) % 90, 90 - abs(angle) % 90)
            if best is None or area_frac > best['areaFrac']:
                best = {
                    'cardDetected': True,
                    'isOrthogonal': ang_dev < ORTHOGONAL_MAX_DEV,
                    'angleDev': round(ang_dev, 1),
                    'areaFrac': round(float(area_frac), 5),
                    'aspectRatio': round(float(ratio), 3),
                }
                best_contour = c

    if best and best_contour is not None:
        rect = cv2.minAreaRect(best_contour)
        ew, eh = rect[1]
        card_px_est = int(max(ew, eh))
        ecx, ecy = int(rect[0][0]), int(rect[0][1])
        half = card_px_est // 2
        if not (ecy - half >= 0 and ecy + half <= h and ecx - half >= 0 and ecx + half <= w):
            best = None
            best_contour = None

    if best:
        return best, best_contour
    # Edge detection failed or contour out of bounds; try colour-based fallback
    return _detect_card_color(img)


def _rect_ortho_dev(rect):
    """Orthogonality deviation (degrees) from minAreaRect."""
    rw, rh = rect[1]
    angle = rect[2]
    if rw < rh:
        angle += 90
    return min(abs(angle) % 90, 90 - abs(angle) % 90)


def _detect_card_color(img):
    """
    Colour-based fallback for cards with distinctive hue
    (e.g., NTU navy-blue student ID in forest scenes).
    Detects either the full card or a header band and rejects
    sky-gap false positives by brightness threshold.
    """
    h, w = img.shape[:2]
    area_total = w * h
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Navy / medium blue: NTU student ID header
    # V < 200 keeps card-in-shadow and card-in-sunlight while
    # rejecting bright sky gaps (V typically > 200)
    mask = cv2.inRange(hsv,
                       np.array([100, 70, 40], dtype=np.uint8),
                       np.array([140, 255, 200], dtype=np.uint8))

    k = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best = None
    best_contour = None
    best_score = -1

    for c in contours:
        area = cv2.contourArea(c)
        area_frac = area / area_total
        if area_frac < 0.001 or area_frac > MAX_AREA_FRAC:
            continue

        rect = cv2.minAreaRect(c)
        rw, rh = sorted(rect[1])
        if rw < 1:
            continue
        ratio = rh / rw

        is_full_card = ASPECT_MIN <= ratio <= ASPECT_MAX
        is_band = 2.5 <= ratio <= 12.0
        if not (is_full_card or is_band):
            continue

        bx, by, bw2, bh2 = cv2.boundingRect(c)
        roi_v = hsv[by:by + bh2, bx:bx + bw2, 2]
        if float(np.mean(roi_v)) > 200:
            continue

        ang_dev = _rect_ortho_dev(rect)
        # bands are smaller; scale score to prefer full-card matches
        score = area_frac * (1.0 if is_full_card else 0.3)

        if score > best_score:
            best_score = score
            best = {
                'cardDetected': True,
                'isOrthogonal': ang_dev < ORTHOGONAL_MAX_DEV,
                'angleDev':     round(ang_dev, 1),
                'areaFrac':     round(float(area_frac), 5),
                'aspectRatio':  round(float(ratio), 3),
            }
            best_contour = c

    if best:
        return best, best_contour
    return {'cardDetected': False, 'isOrthogonal': False, 'angleDev': 90.0,
            'areaFrac': 0.0, 'aspectRatio': 0.0}, None


def process_path(fpath, idx, rotate_cw):
    img = cv2.imread(fpath)
    if img is None:
        return {'path': fpath, 'frameIdx': idx, 'timeSec': 0.0,
                'cardDetected': False, 'isOrthogonal': False,
                'angleDev': 90.0, 'areaFrac': 0.0, 'aspectRatio': 0.0,
                'sharpness': 0.0, 'rotationAngle': 0.0, 'error': 'cannot read'}
    if rotate_cw:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    result, _ = detect_card(img)
    result['sharpness'] = round(_laplacian(img), 1)
    result['rotationAngle'] = 0.0
    result['path'] = fpath
    result['frameIdx'] = idx
    result['timeSec'] = 0.0
    return result

def scan_video(video_path, target_fps, save_dir, rotate_cw):
    """Extract frames via ffmpeg at target_fps, then detect card with OpenCV."""
    os.makedirs(save_dir, exist_ok=True)

    # ffmpeg: extract frames at target_fps, auto-apply rotation metadata
    raw_dir = os.path.join(save_dir, '_raw')
    os.makedirs(raw_dir, exist_ok=True)
    r = subprocess.run(
        ['ffmpeg', '-i', video_path,
         '-vf', f'fps={target_fps}',
         '-q:v', '3',
         os.path.join(raw_dir, 'frame_%04d.jpg'),
         '-y'],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        raise IOError(f'ffmpeg failed: {r.stderr[-300:]}')

    frame_paths = sorted(glob.glob(os.path.join(raw_dir, 'frame_*.jpg')))
    if not frame_paths:
        raise IOError(f'ffmpeg produced no frames from: {video_path}')

    # parse duration from ffmpeg stderr to compute timeSec
    duration_line = [l for l in r.stderr.splitlines() if 'Duration' in l]
    # fallback: estimate from frame count
    results = []
    good_count = 0
    for out_idx, fp in enumerate(frame_paths):
        img = cv2.imread(fp)
        if img is None:
            continue
        if rotate_cw:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

        # resize once here — all subsequent ops use the smaller image
        h, w = img.shape[:2]
        if w > MAX_DETECT_WIDTH:
            scale = MAX_DETECT_WIDTH / w
            img = cv2.resize(img, (MAX_DETECT_WIDTH, int(h * scale)), interpolation=cv2.INTER_AREA)

        result, contour = detect_card(img)
        result['sharpness'] = round(_laplacian(img), 1)
        result['frameIdx'] = out_idx
        result['timeSec'] = round(out_idx / target_fps, 2)

        out_path = os.path.join(save_dir, f'frame_{out_idx}.jpg')
        if result['cardDetected'] and contour is not None:
            rotated, rot_angle = _rotate_to_horizontal(img, contour)
            cv2.imwrite(out_path, rotated, [cv2.IMWRITE_JPEG_QUALITY, 90])
            result['rotationAngle'] = rot_angle
        else:
            cv2.imwrite(out_path, img, [cv2.IMWRITE_JPEG_QUALITY, 85])
            result['rotationAngle'] = 0.0

        result['path'] = out_path
        results.append(result)

        if result['cardDetected'] and result['isOrthogonal']:
            good_count += 1
            if good_count >= EARLY_EXIT_GOOD_FRAMES:
                break

    return results

def main():
    args = sys.argv[1:]
    rotate_cw = False
    if '--rotate-cw' in args:
        rotate_cw = True
        args = [a for a in args if a != '--rotate-cw']

    # Video mode
    if '--video' in args:
        idx = args.index('--video')
        video_path = args[idx + 1]

        target_fps = 2.0
        if '--fps' in args:
            fps_idx = args.index('--fps')
            target_fps = float(args[fps_idx + 1])

        save_dir = None
        if '--save-dir' in args:
            dir_idx = args.index('--save-dir')
            save_dir = args[dir_idx + 1]
        else:
            save_dir = tempfile.mkdtemp(prefix='card_frames_')

        results = scan_video(video_path, target_fps, save_dir, rotate_cw)
        print(json.dumps(results), flush=True)
        return

    # Image mode
    if not args:
        print(json.dumps([]), flush=True)
        return

    results = [process_path(p, i, rotate_cw) for i, p in enumerate(args)]
    print(json.dumps(results), flush=True)

if __name__ == '__main__':
    main()
