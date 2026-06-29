#!/usr/bin/env python3
"""
test_annotated.py — OpenCV 畫校準線後送 Gemini 比對
Usage: python3 scripts/test_annotated.py <frame_path>

Ground truth for IMG_5819 frame_68: p0=21.6cm → expected ratio ≈ 2.52
"""
import sys, os, json, tempfile
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from detect_card import detect_card

CREDITCARD_WIDTH_MM = 85.6

PROMPT = """你是林業測量 AI。

圖上有一條【紅色水平線】，兩端各有紅色圓點。這條紅線的長度精確等於信用卡長邊（85.6mm）。

請回傳：
1. trunkToCardRatio：樹幹在胸高（約 1.3m）的寬度 ÷ 紅線長度的倍數（無法判斷填 0）
2. confidence：信心度 0.0–1.0

規則：
- 紅線是唯一比例尺，只需要數「樹幹寬是幾條紅線」
- 完全忽略畫面中任何文字、數字、捲尺刻度
- 不需要確認卡片是否存在，專注比對紅線與樹幹寬度"""


def draw_calibration_line(img, contour):
    """Draw red horizontal calibration line at card center. Returns (annotated_img, card_px, cx, cy)."""
    rect = cv2.minAreaRect(contour)
    w, h = rect[1]
    card_px = int(max(w, h))
    cx, cy = int(rect[0][0]), int(rect[0][1])

    annotated = img.copy()
    half = card_px // 2
    x1, x2 = cx - half, cx + half

    cv2.line(annotated, (x1, cy), (x2, cy), (0, 0, 255), 5)
    cv2.circle(annotated, (x1, cy), 10, (0, 0, 255), -1)
    cv2.circle(annotated, (x2, cy), 10, (0, 0, 255), -1)
    cv2.putText(annotated, "85.6mm", (cx - 45, cy - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    return annotated, card_px, cx, cy


def call_gemini(img_path, api_key):
    try:
        import google.generativeai as genai
    except ImportError:
        return None, "google-generativeai not installed (pip3 install google-generativeai)"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        generation_config=genai.GenerationConfig(
            response_mime_type='application/json',
            response_schema={
                'type': 'object',
                'properties': {
                    'trunkToCardRatio': {'type': 'number'},
                    'confidence':       {'type': 'number'},
                },
                'required': ['trunkToCardRatio', 'confidence']
            }
        )
    )
    with open(img_path, 'rb') as f:
        data = f.read()

    response = model.generate_content([PROMPT, {'mime_type': 'image/jpeg', 'data': data}])
    return json.loads(response.text), None


def load_api_key():
    key = os.environ.get('GEMINI_API_KEY')
    if key:
        return key
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith('GEMINI_API_KEY='):
                return line.strip().split('=', 1)[1].strip('"\'')
    return None


def main():
    fpath = sys.argv[1] if len(sys.argv) > 1 else None
    if not fpath:
        print("usage: python3 scripts/test_annotated.py <frame_path>")
        sys.exit(1)

    img = cv2.imread(fpath)
    if img is None:
        print(f"cannot read: {fpath}"); sys.exit(1)

    ih, iw = img.shape[:2]
    print(f"frame: {os.path.basename(fpath)}  size={iw}x{ih}")

    result, contour = detect_card(img)

    if not result['cardDetected'] or contour is None:
        print(f"no card detected  result={result}")
        sys.exit(1)

    print(f"card: areaFrac={result['areaFrac']}  aspectRatio={result['aspectRatio']}  "
          f"angleDev={result['angleDev']}  isOrthogonal={result['isOrthogonal']}")

    annotated, card_px, cx, cy = draw_calibration_line(img, contour)
    mm_per_px = CREDITCARD_WIDTH_MM / card_px
    print(f"card_px={card_px}  center=({cx},{cy})  scale={mm_per_px:.4f} mm/px")

    # Save annotated image
    tmp = tempfile.NamedTemporaryFile(suffix='_annotated.jpg', delete=False)
    tmp_path = tmp.name; tmp.close()
    cv2.imwrite(tmp_path, annotated, [cv2.IMWRITE_JPEG_QUALITY, 92])

    # Also save a copy to /tmp for easy retrieval
    out_path = f"/tmp/annotated_{os.path.basename(fpath)}"
    cv2.imwrite(out_path, annotated, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"annotated image → {out_path}")

    api_key = load_api_key()
    if not api_key:
        print("GEMINI_API_KEY not found — annotated image saved above, inspect manually")
        sys.exit(0)

    print("\nsending annotated image to Gemini...")
    result_json, err = call_gemini(tmp_path, api_key)
    os.unlink(tmp_path)

    if err:
        print(f"Gemini error: {err}")
        sys.exit(1)

    ratio = result_json.get('trunkToCardRatio', 0)
    conf  = result_json.get('confidence', 0)
    dbh   = round(ratio * CREDITCARD_WIDTH_MM / 10, 1) if ratio > 0 else None

    print(f"\n--- result (annotated line method) ---")
    print(f"trunkToCardRatio = {ratio}  confidence = {conf}")
    print(f"estimated DBH    = {dbh} cm" if dbh else "DBH = n/a (ratio=0)")

    # Also show what direct pixel measurement would give if trunk width is measured
    # (for reference: if trunk_px were known, DBH = trunk_px * mm_per_px / 10)
    print(f"\n(reference: 1px = {mm_per_px:.3f}mm at this card distance)")


if __name__ == '__main__':
    main()
