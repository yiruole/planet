#!/usr/bin/env python3
"""v03 full grade: vintage-film dream look (ref 01_assets/IMG_1611.PNG).
Interior (f97-504): full milky vintage. Exterior (f1-96, 505-708): same family
but deep blacks kept (the outside stays night). Missing-note sink preserved."""
import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

B = os.path.expanduser("~/Desktop/Digital Art/Borrowed_Music/02_blender")
SRC, OUT = f"{B}/prod", f"{B}/final_v03"
os.makedirs(OUT, exist_ok=True)
names = sorted(n for n in os.listdir(SRC) if n.endswith(".jpg"))
vig = None
for i, n in enumerate(names):
    fr = int(n[1:5])
    interior = 97 <= fr <= 504
    lift = 0.055 if interior else 0.032
    diff_amt = 0.30 if interior else 0.20
    r = np.random.default_rng(fr)
    img = np.asarray(Image.open(os.path.join(SRC, n)).convert("RGB")).astype(np.float32) / 255.0
    h, w = img.shape[:2]
    if vig is None:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r2 = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2
        vig = (1.0 - 0.16 * r2 ** 1.5)[:, :, None]
    lum = img.mean(2)
    halo = gaussian_filter(np.clip(lum - 0.45, 0, 1), 16)
    img = img + halo[:, :, None] * np.array([1.0, 0.86, 0.62]) * 0.45
    soft = gaussian_filter(img, (5.0, 5.0, 0))
    img = 1 - (1 - img * 0.82) * (1 - soft * diff_amt)
    img = img * 0.88 + lift
    img[:, :, 1] += 0.010; img[:, :, 2] += 0.004
    hi = np.clip((lum - 0.55) * 2.2, 0, 1)[:, :, None]
    img += hi * np.array([0.06, 0.045, 0.015])
    img = np.where(img > 0.80, 0.80 + (img - 0.80) * 0.55, img)
    g = img.mean(2, keepdims=True)
    img = img * 0.82 + g * 0.18
    if 680 <= fr <= 688:  # missing-note exposure sink
        img *= 1.0 - 0.22 * np.exp(-((fr - 683) / 2.2) ** 2)
    img *= 1.0 + (r.random() - 0.5) * 0.02
    img += r.standard_normal((h, w, 1)).astype(np.float32) * 0.020
    img += r.standard_normal(img.shape).astype(np.float32) * 0.006
    img *= vig
    Image.fromarray((img.clip(0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, n), quality=93)
    if i % 100 == 0:
        print("v03", i, flush=True)
print("done", len(names))
