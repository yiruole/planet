#!/usr/bin/env python3
"""Borrowed Music — temp sound mix (all TEMP, numpy + macOS say dialogue).
32.5s @44.1k mono. Sync frames (24fps) from SHOT_ASSET_MAP.md."""
import os, wave
import numpy as np

B = os.path.expanduser("~/Desktop/Digital Art/Borrowed_Music/04_sound")
SR = 44100
DUR = 32.5
N = int(SR * DUR)
t = np.arange(N) / SR
mix = np.zeros(N, np.float32)
rng = np.random.default_rng(9)

def sec(fr): return fr / 24.0

def add(sig, at, gain=1.0):
    s = int(at * SR)
    L = min(len(sig), N - s)
    if L > 0: mix[s:s + L] += sig[:L] * gain

def tone(freq, dur, a=0.01, d=0.3, wob=0.0):
    tt = np.arange(int(dur * SR)) / SR
    f = freq * (1 + wob * np.sin(2 * np.pi * 1.3 * tt))
    env = np.minimum(tt / a, 1) * np.exp(-tt / d)
    return np.sin(np.cumsum(2 * np.pi * f / SR)) * env

def noiseband(dur, lp=0.0, hp=False, env_shape=None):
    n = rng.standard_normal(int(dur * SR)).astype(np.float32)
    if hp: n = np.diff(n, prepend=0)
    if lp > 0:
        k = int(lp)
        n = np.convolve(n, np.ones(k) / k, 'same')
    if env_shape is not None: n *= env_shape
    return n

def load(path):
    wf = wave.open(path, 'rb')
    d = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    wf.close(); return d

# ---- bed: low current + equipment hum (whole film, ducked at black) ----
bed = (np.sin(2 * np.pi * 46 * t) * 0.5 + np.sin(2 * np.pi * 92.3 * t) * 0.2)
bed += noiseband(DUR, lp=180) * 0.5
bed *= 0.055
bed[int(29.5 * SR):] *= np.linspace(1, 0, N - int(29.5 * SR))  # fade at black
mix += bed
# distant metal resonance at 2.4s and 5.8s
for at in (2.4, 5.8):
    add(tone(217, 2.2, a=0.15, d=0.9, wob=0.004), at, 0.035)
# faint breath (slow amplitude noise) shots 1-2
br = noiseband(8.0, lp=400)
br *= (0.5 + 0.5 * np.sin(2 * np.pi * 0.24 * np.arange(len(br)) / SR)) ** 2
add(br, 0.5, 0.012)

# ---- S02 wardrobe leak (4.9-13s): several faint musics behind walls ----
leak_t = np.arange(int(8.5 * SR)) / SR
leak = np.zeros(len(leak_t), np.float32)
# loop 1: slow piano pair
for i, at in enumerate(np.arange(0.2, 8.0, 1.9)):
    for j, f0 in enumerate((392, 311)):
        seg = tone(f0, 1.2, a=0.005, d=0.5)
        s = int((at + j * 0.45) * SR)
        e = min(s + len(seg), len(leak)); leak[s:e] += seg[:e - s] * 0.5
# loop 2: choir-ish pad (3 detuned sines, slow)
pad = sum(np.sin(2 * np.pi * f * leak_t + p) for f, p in ((220, 0), (221.5, 1.2), (330, 2.1)))
leak += pad * 0.06 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * leak_t))
# loop 3: static ticks
tick_env = (rng.random(len(leak_t)) < 0.0004).astype(np.float32)
leak += np.convolve(tick_env, np.exp(-np.arange(900) / 200), 'same') * noiseband(8.5, hp=True) * 0.25
# muffle: heavy lowpass + door-opening swell
leak = np.convolve(leak, np.ones(46) / 46, 'same')
sw = np.clip((leak_t - 0.0) / 1.8, 0.12, 1.0)
add(leak * sw, sec(117), 0.30)

# ---- S03 touch sounds (frames 204/230/254/278/298) ----
add(tone(523, 1.0, d=0.6), sec(204), 0.16)  # two piano notes
add(tone(659, 0.9, d=0.5), sec(204) + 0.28, 0.14)
v = tone(230, 0.7, a=0.05, d=0.25, wob=0.02) + tone(690, 0.7, a=0.05, d=0.2, wob=0.03) * 0.4
add(v, sec(230), 0.12)  # brief voice-like formant
pulse = noiseband(0.25, hp=True) * np.exp(-np.arange(int(0.25 * SR)) / (0.03 * SR))
add(pulse, sec(254), 0.14)  # current pulse
mel = np.concatenate([tone(440, 0.5, d=0.35), tone(494, 0.5, d=0.35), tone(392, 0.35, d=0.15)])
add(mel, sec(278), 0.13)  # incomplete childhood melody (cut short)
choir = sum(np.sin(2 * np.pi * f * np.arange(int(1.6 * SR)) / SR) for f in (261.6, 329.6, 392))
choir *= np.minimum(np.arange(int(1.6 * SR)) / (0.7 * SR), 1) * np.exp(-np.arange(int(1.6 * SR)) / (0.9 * SR))
add(np.convolve(choir, np.ones(60) / 60, 'same'), sec(298), 0.035)  # far choir (veil)

# ---- S04 dialogue (TEMP: macOS say) ----
l1 = load(os.path.join(B, "line1.wav"))
add(l1, sec(324), 0.85)
l2 = load(os.path.join(B, "line2.wav"))
l2r = np.diff(l2, prepend=0)  # radio/behind-door: highpass + muffle + quieter
l2r = np.convolve(l2r, np.ones(6) / 6, 'same')
add(l2r, sec(403), 1.4)
# detach whoosh at f468
wh = noiseband(1.1, lp=30)
wh *= np.sin(np.pi * np.arange(len(wh)) / len(wh)) ** 2
add(wh, sec(468), 0.10)

# ---- S05/06 borrowed music: sparse melody, missing note at f682 ----
# melody enters f552 (23.0s): note slots every 0.9s
melody = [(0.0, 392), (0.9, 440), (1.8, 494), (2.7, 392), (3.6, 440), (4.5, 523),
          (5.4, None),   # f682 ≈ 28.4s: the missing note (slot kept, silent)
          (6.3, 392)]
t0 = sec(552)
for off, f0 in melody:
    if f0 is None: continue
    add(tone(f0, 1.6, a=0.008, d=0.8), t0 + off, 0.11)
    add(tone(f0 * 2, 1.2, d=0.4), t0 + off, 0.022)
# rover vibration thump synced to note at f610 (25.4s ~ melody 2nd/3rd note)
add(tone(58, 0.8, a=0.01, d=0.35), sec(610), 0.28)

# ---- master ----
mix *= np.minimum(1, np.arange(N) / (0.3 * SR))
mix = np.tanh(mix * 1.1)
mix16 = (mix / max(1e-9, np.abs(mix).max()) * 0.88 * 32767).astype(np.int16)
wf = wave.open(os.path.join(B, "temp_mix.wav"), 'w')
wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
wf.writeframes(mix16.tobytes()); wf.close()
print("temp_mix.wav", DUR, "s")
