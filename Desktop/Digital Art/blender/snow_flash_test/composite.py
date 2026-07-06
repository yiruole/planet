#!/usr/bin/env python3
"""Assemble the two-state snow scene into the reference's temporal mechanism:

  state A (calm dark) -> audio-drop-synced light-leak flash -> state B
  (front-lit) + 3-depth-layer snowfall + grain.

ffmpeg+numpy only. Usage: python3 composite.py <dir_with_base_A/B> [out.mp4]
"""
import os
import subprocess
import sys

import numpy as np

D = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(D, "snow_flash_mvp.mp4")

FPS = 30
DUR = 8.5
W = H = 720
FLASH_T = 2.2          # matches reference audio drop
FLASH_RAMP = 0.25      # rise to white
FLASH_HOLD = 0.12
FLASH_DECAY = 0.45


def load(p):
    r = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], capture_output=True)
    a = np.frombuffer(r.stdout, np.uint8)
    return a.reshape(H, W, 3).astype(np.float32)


A = load(os.path.join(D, "base_A.png"))
B = load(os.path.join(D, "base_B.png"))


def sky_lift(img, navy, amount):
    luma = img.mean(-1)
    dark = np.clip((46.0 - luma) / 46.0, 0, 1)
    yy2 = np.linspace(0, 1, H)[:, None]
    vert = np.clip((0.62 - yy2) / 0.62, 0, 1) ** 0.8
    m = (dark * vert)[..., None] * amount
    return img + np.array(navy, np.float32) * m


A = sky_lift(A, (26, 52, 148), 1.0)
B = sky_lift(B, (18, 34, 96), 1.0)

# ---------- light-leak wash (warm gradient, magenta->amber, from top) ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
u, v = xx / W, yy / H
amber = np.array([1.00, 0.72, 0.28], np.float32)
magenta = np.array([1.00, 0.35, 0.85], np.float32)
green = np.array([0.55, 1.00, 0.45], np.float32)
w_amber = np.clip(u * 1.3 - 0.15, 0, 1)[..., None]
w_mag = np.clip(1.0 - u * 1.6, 0, 1)[..., None]
w_grn = (np.clip(1.0 - u * 2.2, 0, 1) * np.clip(v * 1.4 - 0.35, 0, 1))[..., None]
wash_col = amber * w_amber + magenta * w_mag + green * w_grn
wash_grad = (np.clip(1.2 - v * 1.05, 0.15, 1) ** 1.3)
WASH = wash_col * wash_grad[..., None] * 255.0

# ---------- snow layers ----------
rng = np.random.default_rng(7)


def make_layer(n, size_px, speed, drift, blur, streak):
    return {
        "x": rng.uniform(0, W, n), "y": rng.uniform(0, H, n),
        "s": rng.uniform(size_px * 0.6, size_px * 1.4, n),
        "spd": rng.uniform(speed * 0.7, speed * 1.3, n),
        "ph": rng.uniform(0, 2 * np.pi, n),
        "drift": drift, "blur": blur, "streak": streak,
    }


def gauss_kernel(sig):
    r = max(int(sig * 3), 1)
    x = np.arange(-r, r + 1, dtype=np.float32)
    k = np.exp(-x**2 / (2 * sig * sig))
    return k / k.sum()


def blur_sep(img, sig):
    if sig <= 0:
        return img
    k = gauss_kernel(sig)
    img = np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 0, img)
    img = np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 1, img)
    return img


layers = [
    make_layer(300, 1.9, 55, 12, 0.0, 4),    # far: small, slight streak
    make_layer(110, 4.2, 115, 24, 1.0, 9),    # mid: streaked
    make_layer(18, 22.0, 75, 34, 6.0, 0),    # near: big soft bokeh
]


def draw_snow(t):
    canvas = np.zeros((H, W), np.float32)
    for L in layers:
        y = (L["y"] + L["spd"] * t) % (H + 60) - 30
        x = (L["x"] + L["drift"] * t + 18 * np.sin(0.7 * t + L["ph"])) % (W + 40) - 20
        lay = np.zeros((H, W), np.float32)
        for xi, yi, si in zip(x, y, L["s"]):
            r = int(si)
            x0, x1 = int(xi) - r, int(xi) + r + 1
            y0, y1 = int(yi) - r, int(yi) + r + 1 + L["streak"]
            if x1 < 0 or y1 < 0 or x0 >= W or y0 >= H:
                continue
            gx = np.arange(max(x0, 0), min(x1, W))
            gy = np.arange(max(y0, 0), min(y1, H))
            if len(gx) == 0 or len(gy) == 0:
                continue
            dx = (gx - xi) / max(si, 1)
            dy = (gy - yi - L["streak"] * 0.5) / max(si + L["streak"] * 0.6, 1)
            spot = np.exp(-(dx[None, :]**2 + dy[:, None]**2) * 2.2)
            lay[np.ix_(gy, gx)] = np.maximum(lay[np.ix_(gy, gx)], spot)
        if L["blur"] > 0:
            lay = blur_sep(lay, L["blur"])
        canvas = np.maximum(canvas, lay * (0.80 if L["blur"] > 3 else 0.95))
    return canvas


def flash_amount(t):
    if t < FLASH_T:
        return 0.0
    if t < FLASH_T + FLASH_RAMP:
        return ((t - FLASH_T) / FLASH_RAMP) ** 1.6
    if t < FLASH_T + FLASH_RAMP + FLASH_HOLD:
        return 1.0
    d = t - (FLASH_T + FLASH_RAMP + FLASH_HOLD)
    return max(0.0, 1.0 - d / FLASH_DECAY) ** 1.3


N = int(DUR * FPS)
enc = subprocess.Popen(
    ["ffmpeg", "-v", "quiet", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
     "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", OUT],
    stdin=subprocess.PIPE)

reveal_t = FLASH_T + FLASH_RAMP + FLASH_HOLD   # B revealed as flash decays
for i in range(N):
    t = i / FPS
    if t < reveal_t:
        frame = A * np.array([0.60, 0.72, 1.06], np.float32) * 0.82
    else:
        frame = B.copy()

    if t >= reveal_t:
        # snowfall only in state B
        snow = draw_snow(t - reveal_t + 3.0)
        frame = np.maximum(frame, snow[..., None] * np.arra