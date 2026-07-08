#!/usr/bin/env python3
"""STAGE 3 compositing: gentle imaging chain over hero base renders
(HALO->SOFT->CHROMA->TONE->GRAIN->vignette, tuned darker/cooler than phase6)."""
import os, sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

rng = np.random.default_rng(7)

def comp(src, dst):
    img = np.asarray(Image.open(src).convert("RGB")).astype(np.float32) / 255.0
    h, w = img.shape[:2]
    lum = img.mean(2)
    halo = gaussian_filter(np.clip(lum - 0.55, 0, 1), 14)
    img = img + halo[:, :, None] * np.array([0.75, 0.82, 1.0]) * 0.35
    img = img * 0.45 + gaussian_filter(img, (0.9, 0.9, 0)) * 0.55
    img += rng.standard_normal(img.shape).astype(np.float32) * 0.008
    img = img * 0.96 + 0.018                       # gentle black lift to blue-gray
    img[:, :, 2] *= 1.03; img[:, :, 0] *= 0.985    # cool cast
    img = np.where(img > 0.82, 0.82 + (img - 0.82) * 0.7, img)
    img += rng.standard_normal((h, w, 1)).astype(np.float32) * 0.013
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r2 = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2
    img *= (1.0 - 0.22 * r2 ** 1.3)[:, :, None]
    Image.fromarray((img.clip(0, 1) * 255).astype(np.uint8)).save(dst)
    print("comp:", os.path.basename(dst))

B = os.path.expanduser("~/Desktop/Digital Art/Borrowed_Music/04_lookdev")
comp(f"{B}/S02/S02_base.png", f"{B}/S02/S02_hero_comp.png")
for st in "abc":
    comp(f"{B}/S04/S04_{st}_base.png", f"{B}/S04/S04_{st}_comp.png")
