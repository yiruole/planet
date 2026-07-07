#!/usr/bin/env python3
"""video2 MVP: 'living painting' — time-varying displacement of the oil-painting
surface only (frame + wall stay static), mimicking ref2's continuous texture
rearrangement. Output: jpg frames -> ffmpeg assembles 4s/30fps clip."""
import os, sys
import numpy as np
from PIL import Image
from scipy.ndimage import zoom, map_coordinates

BASE = os.path.expanduser("~/Desktop/Digital Art/AE/video2/results/mvp")
img = np.asarray(Image.open(os.path.join(BASE, "base_frame.png"))).astype(np.float32)
H, W = img.shape[:2]
print("base", W, "x", H)

# work at half res for speed
img_s = np.asarray(Image.fromarray(img.astype(np.uint8)).resize((W // 2, H // 2), Image.LANCZOS)).astype(np.float32)
h, w = img_s.shape[:2]

# painting inner-canvas rect as fractions of full frame (measured on preview):
# preview 720x1280: canvas x 18..690, y 300..880
x0, x1 = int(0.068 * w), int(0.912 * w)
y0, y1 = int(0.275 * h), int(0.648 * h)

# soft mask: 1 inside canvas, tight feather so the gilt frame never moves
mask = np.zeros((h, w), np.float32)
mask[y0:y1, x0:x1] = 1.0
from scipy.ndimage import gaussian_filter
mask = gaussian_filter(mask, 7)
mask[mask > 1] = 1

N = 120           # 4s @ 30fps
KEY_EVERY = 9
AMP = 9.0
GRID = (10, 6)    # coarse noise grid (rows, cols)

rng = np.random.default_rng(7)
nkeys = N // KEY_EVERY + 2
keys = rng.uniform(-1, 1, (nkeys, 2, *GRID)).astype(np.float32)

yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
os.makedirs(os.path.join(BASE, "frames"), exist_ok=True)

for f in range(N):
    k = f / KEY_EVERY
    i = int(k)
    t = k - i
    t = t * t * (3 - 2 * t)  # smoothstep between keyfields
    field = (1 - t) * keys[i] + t * keys[i + 1]
    dx = zoom(field[0], (h / GRID[0], w / GRID[1]), order=3, mode="nearest")[:h, :w]
    dy = zoom(field[1], (h / GRID[0], w / GRID[1]), order=3, mode="nearest")[:h, :w]
    dx = dx * AMP * mask
    dy = dy * AMP * 0.7 * mask
    coords = np.stack([yy + dy, xx + dx])
    out = np.empty_like(img_s)
    for c in range(img_s.shape[2]):
        out[:, :, c] = map_coordinates(img_s[:, :, c], coords, order=1, mode="nearest")
    Image.fromarray(out.astype(np.uint8)).save(os.path.join(BASE, "frames", "f%04d.jpg" % f), quality=92)
    if f % 30 == 0:
        print("frame", f)
print("done", N, "frames at", w, "x", h)
