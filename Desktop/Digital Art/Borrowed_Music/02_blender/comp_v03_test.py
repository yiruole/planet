#!/usr/bin/env python3
"""v03 look test: vintage-film dream grade (ref: 01_assets/IMG_1611.PNG —
1950s-60s Chinese studio color film). Elements: diffusion glow, milky lifted
blacks (green-cyan), cream highlight rolloff, desaturation, coarse grain,
warm halation. Test on 3 frames, side-by-side with v02."""
import os, sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

B = os.path.expanduser("~/Desktop/Digital Art/Borrowed_Music/02_blender")
rng = np.random.default_rng(3)

def grade_v03(img, seed=0):
    r = np.random.default_rng(seed)
    h, w = img.shape[:2]
    # 1. warm halation from highlights
    lum = img.mean(2)
    halo = gaussian_filter(np.clip(lum - 0.45, 0, 1), 16)
    img = img + halo[:, :, None] * np.array([1.0, 0.86, 0.62]) * 0.45
    # 2. dreamy diffusion: screen-blend a heavy blur (蒙纱)
    soft = gaussian_filter(img, (5.0, 5.0, 0))
    img = 1 - (1 - img * 0.82) * (1 - soft * 0.30)
    # 3. milky lifted blacks w/ green-cyan; cream highlights
    img = img * 0.88 + 0.055
    img[:, :, 1] += 0.010; img[:, :, 2] += 0.004          # green-cyan floor
    hi = np.clip((lum - 0.55) * 2.2, 0, 1)[:, :, None]
    img += hi * np.array([0.06, 0.045, 0.015])            # cream top
    img = np.where(img > 0.80, 0.80 + (img - 0.80) * 0.55, img)
    # 4. desaturate 18% + slight overall fade
    g = img.mean(2, keepdims=True)
    img = img * 0.82 + g * 0.18
    # 5. coarse grain + slight luma flicker
    img *= 1.0 + (r.random() - 0.5) * 0.02
    img += r.standard_normal((h, w, 1)).astype(np.float32) * 0.020
    img += r.standard_normal(img.shape).astype(np.float32) * 0.006
    # 6. soft vignette
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r2 = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2
    img *= (1.0 - 0.16 * r2 ** 1.5)[:, :, None]
    return img.clip(0, 1)

for fr in (150, 470, 600):
    src = np.asarray(Image.open(f"{B}/prod/f{fr:04d}.jpg").convert("RGB")).astype(np.float32) / 255.0
    v03 = grade_v03(src, seed=fr)
    v02 = np.asarray(Image.open(f"{B}/final/f{fr:04d}.jpg").convert("RGB")).astype(np.float32) / 255.0
    pair = np.concatenate([v02, v03], axis=1)
    Image.fromarray((pair * 255).astype(np.uint8)).save(f"{B}/v03_test_f{fr}.png")
    print("test", fr)
