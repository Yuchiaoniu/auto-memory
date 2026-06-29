#!/usr/bin/env python3
import cv2, os, glob, sys

frames_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/test_5819/frames"
paths = sorted(glob.glob(f"{frames_dir}/frame_*.jpg"),
               key=lambda p: int(os.path.basename(p).split("_")[1].split(".")[0]))

print(f"total frames: {len(paths)}")
for fp in paths[:5]:
    img = cv2.imread(fp)
    h, w = img.shape[:2]
    print(f"  {os.path.basename(fp)}: {w}x{h}")

print(f"  ...")
for fp in paths[-3:]:
    img = cv2.imread(fp)
    h, w = img.shape[:2]
    print(f"  {os.path.basename(fp)}: {w}x{h}")

fp68 = f"{frames_dir}/frame_68.jpg"
if os.path.exists(fp68):
    img = cv2.imread(fp68)
    h, w = img.shape[:2]
    print(f"\nframe_68.jpg: {w}x{h}")
else:
    print(f"\nframe_68.jpg NOT FOUND (total={len(paths)}, last={os.path.basename(paths[-1]) if paths else 'none'})")
