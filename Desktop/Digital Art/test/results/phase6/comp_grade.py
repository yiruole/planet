#!/usr/bin/env python3
"""Phase 6 compositing stage (AE-role, offline): imaging chain over the Blender
blocking render. Order (verified in TD backrooms case): HALO -> SOFT -> CHROMA
-> TONE -> GRAIN -> vignette. numpy+scipy, 300 frames."""
import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

BASE = os.path.expanduser("~/Desktop/Digital Art/test/results/phase6")
SRC, OUT = os.path.join(BASE, "anim"), os.path.join(BASE, "final")
os.makedirs(OUT, exist_ok=True)
names = sorted(n for n in os.listdir(SRC) if n.endswith(".jpg"))
rng = np.random.default_rng(5)

h = w = None
vig = None
for i, n in enumerate(names):
    img = np.asarray(Image.open(os.path.join(SRC, n))).astype(np.float32) / 255.0
    if vig is None:
        h, w = img.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r2 = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2
        vig = 1.0 - 0.28 * r2 ** 1.2
    # HALO: warm bloom from highlights
    lum = img.mean(2)
    hi = np.clip(lum - 0.72, 0, 1)
    halo = gaussian_filter(hi, 18)
    img = img + halo[:, :, None] * np.array([1.0, 0.75, 0.45]) * 0.5
    # SOFT: eat CG edges
    img = img * 0.35 + gaussian_filter(img, (1.1, 1.1, 0)) * 0.65
    # CHROMA noise
    img += rng.standard_normal(img.shape).astype(np.float32) * 0.012
    # TONE: black lift + highlight rolloff
    img = img * 0.94 + 0.035
    img = np.where(img > 0.8, 0.8 + (img - 0.8) * 0.65, img)
    # GRAIN (mono)
    img += rng.standard_normal((h, w, 1)).astype(np.float32) * 0.022
    # vignette
    img *= vig[:, :, None]
    Image.fromarray((img.clip(0, 1) * 255).astype(np.uint8)).save(
        os.path.join(OUT, n), quality=93)
    if i % 60 == 0:
        print("frame", i, flush=True)
print("done", len(names))
