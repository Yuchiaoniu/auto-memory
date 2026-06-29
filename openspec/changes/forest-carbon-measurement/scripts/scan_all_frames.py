#!/usr/bin/env python3
"""Scan all frames in a directory and print detection results, sorted by quality."""
import cv2, os, glob, sys, json
sys.path.insert(0, '/home/yuchi/forest-carbon-measurement/scripts')
from detect_card import detect_card

frames_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/test_5819/frames"

paths = sorted(glob.glob(f"{frames_dir}/frame_*.jpg"),
               key=lambda p: int(os.path.basename(p).split("_")[1].split(".")[0]))

print(f"Scanning {len(paths)} frames in {frames_dir}")

good = []
for fp in paths:
    img = cv2.imread(fp)
    if img is None:
        continue
    h, w = img.shape[:2]
    result, contour = detect_card(img)
    if not result['cardDetected'] or contour is None:
        continue
    import cv2 as _cv2
    rect = _cv2.minAreaRect(contour)
    ew, eh = rect[1]
    card_px = int(max(ew, eh))
    cx, cy = int(rect[0][0]), int(rect[0][1])
    half = card_px // 2
    in_bounds = (cy - half >= 0 and cy + half <= h and cx - half >= 0 and cx + half <= w)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lap = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    good.append({
        'frame': os.path.basename(fp),
        'cx': cx, 'cy': cy, 'card_px': card_px,
        'in_bounds': in_bounds,
        'areaFrac': result['areaFrac'],
        'angleDev': result['angleDev'],
        'isOrth': result['isOrthogonal'],
        'sharpness': round(lap, 1),
    })

print(f"\nDetected {len(good)} frames with card")
print(f"In-bounds: {sum(1 for g in good if g['in_bounds'])}")
print(f"\n{'Frame':<12} {'cx':>5} {'cy':>5} {'card_px':>8} {'inBounds':>9} {'aFrac':>7} {'angDev':>7} {'sharp':>8}")
for g in sorted(good, key=lambda x: (-int(x['in_bounds']), -x['sharpness'])):
    print(f"{g['frame']:<12} {g['cx']:>5} {g['cy']:>5} {g['card_px']:>8} {str(g['in_bounds']):>9} {g['areaFrac']:>7.4f} {g['angleDev']:>7.1f} {g['sharpness']:>8.1f}")
