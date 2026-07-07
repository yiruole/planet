#!/usr/bin/env python3
"""Phase 5 animatic: photo-state previs from 2.imagetovideo.JPG.
Shot A (5s): gold->dusk diagonal shadow sweep. Shot B (3s): door insert,
last light patch shrinks. Shot C (4s): night grade + lantern glow pools +
transient-driven flicker. Assembled at 30fps, 1080x720."""
import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

T = os.path.expanduser("~/Desktop/Digital Art/test")
OUT = os.path.join(T, "results/phase5")
os.makedirs(os.path.join(OUT, "frames"), exist_ok=True)

photo = Image.open(os.path.join(T, "2.imagetovideo.JPG"))
W, H = 1080, 720
day = np.asarray(photo.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255.0

def grade_dusk(img):
    g = img * 0.42
    g[:, :, 2] *= 1.18; g[:, :, 0] *= 0.92
    return g

def grade_night(img):
    g = img * 0.16
    g[:, :, 2] *= 1.45; g[:, :, 1] *= 1.05; g[:, :, 0] *= 0.72
    return g

dusk = grade_dusk(day)
night = grade_night(day)

# lantern glow pools (two wall lanterns, coords in 1080x720 from photo)
LAMPS = [(186, 345), (770, 352)]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
def glow(cx, cy, r):
    d2 = ((xx - cx) ** 2 + (yy - cy) ** 2) / (r * r)
    return np.exp(-d2)

glows = [glow(cx, cy, 110) for cx, cy in LAMPS]
warm = np.array([1.0, 0.62, 0.28])

# diagonal sweep mask: shadow boundary moves lower-left -> upper-right
diag = (xx / W + (1 - yy / H))  # 0 bottom-left .. 2 top-right

FPS = 30
frames = []

# --- Shot A: 5s sweep gold->dusk ---
NA = 150
for f in range(NA):
    t = f / (NA - 1)
    thresh = 0.15 + 1.9 * t
    m = np.clip((diag - thresh) / 0.08, 0, 1)[:, :, None]  # 1 = still sunlit
    img = dusk * (1 - m) + day * m
    frames.append(img)

# --- Shot B: 3s door insert, patch shrinks (crop center door region) ---
NB = 90
cx0, cy0, cw, ch = 380, 180, 405, 270  # crop rect on 1080x720
for f in range(NB):
    t = f / (NB - 1)
    thresh = 1.35 + 0.75 * t
    m = np.clip((diag - thresh) / 0.05, 0, 1)[:, :, None]
    img = dusk * (1 - m) + day * m
    crop = img[cy0:cy0 + ch, cx0:cx0 + cw]
    img_b = np.asarray(Image.fromarray((crop * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(np.float32) / 255.0
    frames.append(img_b)

# --- Shot C: 4s night, lamps wake (left first, right +0.8s), glitch flicker ---
NC = 120
rng = np.random.default_rng(3)
# sparse transient times after both lamps on
tr_frames = sorted(rng.choice(np.arange(45, NC - 5), 7, replace=False))
flick = np.zeros(NC)
for tf in tr_frames:
    k = np.exp(-np.arange(8) / 2.0) * (0.3 if rng.random() < 0.7 else -0.45)
    flick[tf:tf + 8] += k[:max(0, min(8, NC - tf))]
for f in range(NC):
    on0 = np.clip((f - 8) / 6.0, 0, 1)
    on1 = np.clip((f - 32) / 6.0, 0, 1)
    img = night.copy()
    for on, g in zip((on0, on1), glows):
        amp = on * (1.0 + flick[f])
        img += g[:, :, None] * warm[None, None, :] * 0.55 * max(0.0, amp)
    frames.append(img)

for i, img in enumerate(frames):
    Image.fromarray((img.clip(0, 1) * 255).astype(np.uint8)).save(
        os.path.join(OUT, "frames", "f%04d.jpg" % i), quality=90)
print("frames", len(frames))

# storyboard stills
for name, idx in (("sb_A", 40), ("sb_B", NA + 60), ("sb_C", NA + NB + 70)):
    Image.fromarray((frames[idx].clip(0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, name + ".jpg"), quality=92)
print("storyboard saved")
