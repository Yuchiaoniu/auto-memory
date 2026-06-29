#!/usr/bin/env python3
import cv2, sys, json, math
import numpy as np
sys.path.insert(0, '/home/yuchi/forest-carbon-measurement/scripts')
from detect_card import detect_card, _detect_card_color

img = cv2.imread('/tmp/test_5819/frames/frame_68.jpg')
h, w = img.shape[:2]
print(f"img: {w}x{h}")

area_total = w * h
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)

print("=== edge detection candidates ===")
for lo, hi in [(30, 100), (50, 150), (10, 60)]:
    edges = cv2.Canny(blur, lo, hi)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.dilate(edges, kernel, iterations=1)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        area = cv2.contourArea(c)
        area_frac = area / area_total
        if area_frac < 0.004 or area_frac > 0.50:
            continue
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.03 * peri, True)
        rect = cv2.minAreaRect(c)
        rw, rh = sorted(rect[1])
        if rw < 1:
            continue
        ratio = rh / rw
        if not (1.4 <= ratio <= 1.8):
            continue
        ecx, ecy = int(rect[0][0]), int(rect[0][1])
        ew, eh = rect[1]
        card_px_est = int(max(ew, eh))
        half = card_px_est // 2
        in_bounds = (ecy - half >= 0 and ecy + half <= h and ecx - half >= 0 and ecx + half <= w)
        print(f"  edge({lo},{hi}): cx={ecx} cy={ecy} card_px={card_px_est} areaFrac={area_frac:.5f} ratio={ratio:.3f} in_bounds={in_bounds} pts={len(approx)}")

print("=== color detection ===")
result, contour = _detect_card_color(img)
if contour is not None:
    rect = cv2.minAreaRect(contour)
    ew, eh = rect[1]
    card_px = int(max(ew, eh))
    ecx, ecy = int(rect[0][0]), int(rect[0][1])
    half = card_px // 2
    in_bounds = (ecy - half >= 0 and ecy + half <= h and ecx - half >= 0 and ecx + half <= w)
    print(f"  cx={ecx} cy={ecy} card_px={card_px} areaFrac={result['areaFrac']} aspectRatio={result['aspectRatio']} in_bounds={in_bounds}")
else:
    print("  no color detection")

print("=== full detect_card result ===")
result2, contour2 = detect_card(img)
print(f"  cardDetected={result2['cardDetected']}")
if contour2 is not None:
    rect = cv2.minAreaRect(contour2)
    ew, eh = rect[1]
    card_px = int(max(ew, eh))
    ecx, ecy = int(rect[0][0]), int(rect[0][1])
    half = card_px // 2
    in_bounds = (ecy - half >= 0 and ecy + half <= h and ecx - half >= 0 and ecx + half <= w)
    print(f"  cx={ecx} cy={ecy} card_px={card_px} in_bounds={in_bounds}")
