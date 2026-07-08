#!/usr/bin/env python3
"""STAGE 4: imaging chain over production frames (gentle: halo/soft/chroma/
tone/grain/vignette) + extra picture response at the missing note (f682:
one-frame-family exposure sink, comp-side, subtle but visible)."""
import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

B = os.path.expanduser("~/Desktop/Digital Art/Borrowed_Music/02_blender")
SRC, OUT = f"{B}/prod", f"{B}/final"
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(11)
names = sorted(n for n in os.listdir(SRC) if n.endswith(".jpg"))
vig = None
for i, n in enumerate(names):
    fr = int(n[1:5])
    img = np.asarray(Image.open(os.path.join(SRC, n)).convert("RGB")).astype(np.float32) / 255.0
    h, w = img.shape[:2]
    if vig is None:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r2 = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2
        vig = (1.0 - 0.22 * r2 ** 1.3)[:, :, None]
    lum = img.mean(2)
    halo = gaussian_filter(np.clip(lum - 0.55, 0, 1), 12)
    img = img + halo[:, :, None] * np.array([0.75, 0.82, 1.0]) * 0.32
    img = img * 0.45 + gaussian_filter(img, (0.9, 0.9, 0)) * 0.55
    img += rng.standard_normal(img.shape).astype(np.float32) * 0.007
    img = img * 0.96 + 0.016
    img[:, :, 2] *= 1.03; img[:, :, 0] *= 0.985
    img = np.where(img > 0.82, 0.82 + (img - 0.82) * 0.7, img)
    # missing-note response: exposure sink over 6 frames around f682
    if 680 <= fr <= 688:
        k = 1.0 - 0.22 * np.exp(-((fr - 683) / 2.2) ** 2)
        img *= k
    img += rng.standard_normal((h, w, 1)).astype(np.float32) * 0.012
    img *= vig
    Image.fromarray((img.clip(0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, n), quality=93)
    if i % 100 == 0:
        print("comp", i, flush=True)
print("done", len(names))
