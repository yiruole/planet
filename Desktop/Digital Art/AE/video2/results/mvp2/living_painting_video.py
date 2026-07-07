#!/usr/bin/env python3
"""Phase 2 transfer test v2: living-painting recipe on VIDEO.
Pipeline: phase-correlation global translation tracking -> stabilization
(painting/wall truly static) -> Phase-1 masked key-field displacement.
Finding baked in: breathing (~2.5 motion units) drowns under camera motion
(13-55 units), so the mechanism requires a stabilized substrate."""
import os
import numpy as np
from PIL import Image
from scipy.ndimage import zoom, map_coordinates, gaussian_filter

BASE = os.path.expanduser("~/Desktop/Digital Art/AE/video2/results/mvp2")
SRC, OUT = os.path.join(BASE, "src"), os.path.join(BASE, "frames")
os.makedirs(OUT, exist_ok=True)
names = sorted(os.listdir(SRC))
N = len(names)

def load(i):
    return np.asarray(Image.open(os.path.join(SRC, names[i]))).astype(np.float32)

h, w = load(0).shape[:2]

# --- 1. phase-correlation translation per consecutive pair, accumulated ---
def gray_small(img):
    g = img.mean(2)
    return g[::4, ::4]  # 240x135

def phasecorr(a, b):
    wa = np.outer(np.hanning(a.shape[0]), np.hanning(a.shape[1]))
    FA, FB = np.fft.rfft2(a * wa), np.fft.rfft2(b * wa)
    R = FA * np.conj(FB)
    R /= np.abs(R) + 1e-9
    r = np.fft.irfft2(R, a.shape)
    py, px = np.unravel_index(np.argmax(r), r.shape)
    if py > a.shape[0] // 2: py -= a.shape[0]
    if px > a.shape[1] // 2: px -= a.shape[1]
    return px, py

offs = [(0.0, 0.0)]
prev = gray_small(load(0))
for i in range(1, N):
    cur = gray_small(load(i))
    dx, dy = phasecorr(prev, cur)  # shift of cur relative to prev
    offs.append((offs[-1][0] + dx * 4, offs[-1][1] + dy * 4))
    prev = cur
offs = np.array(offs)
print("track range x", offs[:, 0].min(), offs[:, 0].max(), "y", offs[:, 1].min(), offs[:, 1].max())

# --- 2. displacement field engine (Phase-1 recipe) ---
# painting inner-canvas rect, same fractions as Phase 1 (framing at 0-3s matches)
x0, x1 = int(0.068 * w), int(0.912 * w)
y0, y1 = int(0.275 * h), int(0.648 * h)
mask = np.zeros((h, w), np.float32)
mask[y0:y1, x0:x1] = 1.0
mask = gaussian_filter(mask, 7); mask[mask > 1] = 1

KEY_EVERY = 9; AMP = 9.0; GRID = (10, 6)
rng = np.random.default_rng(7)
keys = rng.uniform(-1, 1, (N // KEY_EVERY + 2, 2, *GRID)).astype(np.float32)
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)

for f in range(N):
    img = load(f)
    ox, oy = offs[f]
    k = f / KEY_EVERY
    i = int(k); t = k - i; t = t * t * (3 - 2 * t)
    field = (1 - t) * keys[i] + t * keys[i + 1]
    ddx = zoom(field[0], (h / GRID[0], w / GRID[1]), order=3, mode="nearest")[:h, :w] * AMP * mask
    ddy = zoom(field[1], (h / GRID[0], w / GRID[1]), order=3, mode="nearest")[:h, :w] * AMP * 0.7 * mask
    # single resample: output(stabilized+displaced) samples source at
    # stab offset (+ox,+oy in source coords) plus breathing displacement
    coords = np.stack([yy + oy + ddy, xx + ox + ddx])
    out = np.empty_like(img)
    for c in range(img.shape[2]):
        out[:, :, c] = map_coordinates(img[:, :, c], coords, order=1, mode="nearest")
    # exposure lock: iPhone auto-exposure pumps global luma; normalize gain
    # against a wall patch (static, out of painting) so only the canvas moves
    wall = out[60:160, :, :].mean()
    if f == 0:
        wall_ref = wall
    out *= wall_ref / max(wall, 1e-6)
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(os.path.join(OUT, "f%04d.jpg" % f), quality=92)
    if f % 30 == 0:
        print("frame", f, flush=True)
print("done", N)
