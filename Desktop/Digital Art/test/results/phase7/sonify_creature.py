#!/usr/bin/env python3
"""Phase 7: physical-phenomena sonification. Blackwater larval fish (translucent,
wing-like fins, pulsing against black) -> structural variables -> sound.
Variables (4): fin-spread area, centroid velocity, boundary complexity, pulse phase.
Mapping: area->spectral width+grain density, velocity->event rate, complexity->
harmonic count, silence preserved when creature drifts. Pure numpy synthesis."""
import os, json, subprocess
import numpy as np
from PIL import Image

T = os.path.expanduser("~/Desktop/Digital Art/test")
OUT = os.path.join(T, "results/phase7")
SRC = os.path.join(OUT, "src")
os.makedirs(SRC, exist_ok=True)

# 1. extract frames, crop UI (center black-water region)
if not os.path.exists(os.path.join(SRC, "f0001.jpg")):
    subprocess.run(["ffmpeg", "-y", "-i", os.path.join(T, "4.physical-phenomena-sonification.mov"),
                    "-vf", "crop=iw*0.82:ih*0.55:0:ih*0.17,scale=290:395,fps=30",
                    "-q:v", "3", os.path.join(SRC, "f%04d.jpg")],
                   capture_output=True)
names = sorted(os.listdir(SRC))[18:]  # drop reel-swipe transition (contaminated)
N = len(names)
print("frames", N)

area = np.zeros(N); cx = np.zeros(N); cy = np.zeros(N); comp = np.zeros(N)
for i, n in enumerate(names):
    g = np.asarray(Image.open(os.path.join(SRC, n)).convert("L")).astype(np.float32)
    m = g > 26
    a = m.sum()
    area[i] = a
    if a > 40:
        ys, xs = np.nonzero(m)
        cx[i], cy[i] = xs.mean(), ys.mean()
        gy, gx = np.gradient(m.astype(np.float32))
        per = (np.abs(gy) + np.abs(gx)).sum()
        comp[i] = per / (2 * np.sqrt(np.pi * a))  # 1.0 = circle, higher = complex
    else:
        cx[i], cy[i] = cx[i - 1], cy[i - 1]

vel = np.hypot(np.diff(cx, prepend=cx[0]), np.diff(cy, prepend=cy[0]))
vel = np.convolve(vel, np.ones(5) / 5, 'same')
area_n = (area - np.percentile(area, 5)) / (np.percentile(area, 98) - np.percentile(area, 5) + 1e-9)
area_n = area_n.clip(0, 1)
vel_n = (vel / (np.percentile(vel, 95) + 1e-9)).clip(0, 1.4)
comp_n = ((comp - 1.5) / 6.0).clip(0, 1)

# pulse period from area autocorrelation
a0 = area_n - area_n.mean()
ac = np.correlate(a0, a0, 'full')[N:]
period = int(np.argmax(ac[8:90]) + 8)
print("pulse period frames:", period)

np.savez(os.path.join(OUT, "variables.npz"), area=area_n, vel=vel_n, comp=comp_n, period=period)
json.dump({"n_frames": int(N), "fps": 30, "pulse_period_s": round(period / 30, 3),
           "area_range_px": [int(area.min()), int(area.max())],
           "complexity_range": [round(float(comp.min()), 2), round(float(comp.max()), 2)]},
          open(os.path.join(OUT, "variables.json"), "w"), indent=1)

# 2. synthesis (44.1k): breathing additive drone + motion grains
SR = 44100
dur = N / 30.0
t = np.arange(int(dur * SR)) / SR
fidx = np.minimum((t * 30).astype(int), N - 1)
A = area_n[fidx]          # per-sample control curves
V = vel_n[fidx]
C = comp_n[fidx]

base = 110.0  # A2 drone root
audio = np.zeros_like(t)
# harmonic stack: count follows complexity, spread follows area
for h in range(1, 9):
    on = (C * 8 >= h - 1).astype(np.float32)          # more harmonics when complex
    detune = 1.0 + 0.012 * (h - 1) * A                # area widens the spectrum
    amp = on * (A ** 0.7) * (0.5 / h)
    phase = np.cumsum(2 * np.pi * base * h * detune / SR)
    audio += amp * np.sin(phase)
# sub pulse locked to fin period
pulse = 0.5 * (1 + np.sin(2 * np.pi * t * (30.0 / period) - np.pi / 2))
audio *= 0.35 + 0.65 * pulse ** 1.5
# motion grains: velocity spawns filtered noise ticks
rng = np.random.default_rng(11)
grain_env = np.zeros_like(t)
vf = vel_n.copy()
for i in range(N):
    if vf[i] > 0.5 and rng.random() < vf[i] * 0.5:
        s = int(i / 30 * SR)
        L = int(0.05 * SR)
        if s + L < len(t):
            grain_env[s:s + L] += np.exp(-np.arange(L) / (0.012 * SR)) * vf[i]
noise = rng.standard_normal(len(t)) * 0.25
# simple bandpass via diff (high) mixed with smoothed (low)
hp = np.diff(noise, prepend=0)
audio += grain_env * hp * 0.8
# gentle master envelope + normalize
audio *= np.minimum(1, t * 4) * np.minimum(1, (dur - t) * 4)
audio = np.tanh(audio * 1.4)
audio16 = (audio / max(1e-9, np.abs(audio).max()) * 0.9 * 32767).astype(np.int16)

import wave
wf = wave.open(os.path.join(OUT, "creature_sonified.wav"), "w")
wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
wf.writeframes(audio16.tobytes()); wf.close()
print("wav written", round(dur, 2), "s")

# 3. variable curve panel
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    tt = np.arange(N) / 30
    fig, axs = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
    axs[0].plot(tt, area_n); axs[0].set_ylabel("fin area")
    axs[1].plot(tt, vel_n); axs[1].set_ylabel("velocity")
    axs[2].plot(tt, comp_n); axs[2].set_ylabel("complexity"); axs[2].set_xlabel("s")
    fig.suptitle(f"creature variables (pulse {period/30:.2f}s)")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "variables_panel.png"), dpi=110)
    print("panel saved")
except Exception as e:
    print("plot skipped", e)
