#!/usr/bin/env python3
"""Phase 4: audio feature extraction (numpy only). Outputs features.npz +
features.json (summary) + feature_panel.png (visual evidence)."""
import json, os, wave
import numpy as np

BASE = os.path.expanduser("~/Desktop/Digital Art/test/results/phase4")
wf = wave.open(os.path.join(BASE, "sound.wav"), 'rb')
sr = wf.getframerate()
x = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
wf.close()
dur = len(x) / sr
print("sr", sr, "dur %.2f" % dur)

FPS = 30
hop = sr // FPS                 # one feature frame per video frame
win = 2048
nfrm = (len(x) - win) // hop
hann = np.hanning(win)
freqs = np.fft.rfftfreq(win, 1 / sr)

mag = np.empty((nfrm, len(freqs)), np.float32)
for i in range(nfrm):
    seg = x[i * hop:i * hop + win] * hann
    mag[i] = np.abs(np.fft.rfft(seg))

def band(lo, hi):
    m = (freqs >= lo) & (freqs < hi)
    return mag[:, m].sum(1)

rms = np.sqrt((mag ** 2).sum(1)) / win
low, mid, high = band(20, 200), band(200, 2000), band(2000, 10000)
centroid = (mag * freqs).sum(1) / (mag.sum(1) + 1e-9)
flux = np.maximum(mag[1:] - mag[:-1], 0).sum(1)
flux = np.concatenate([[0], flux])
flux_n = flux / (flux.max() + 1e-9)
# transient mask: flux peaks above adaptive threshold
med = np.convolve(flux_n, np.ones(15) / 15, mode='same')
transient = (flux_n > med * 1.8) & (flux_n > 0.12)
silence = rms < (rms.max() * 0.06)
# repetition: autocorrelation of flux envelope -> dominant period
ac = np.correlate(flux_n - flux_n.mean(), flux_n - flux_n.mean(), 'full')[len(flux_n):]
period = int(np.argmax(ac[10:150]) + 10)  # frames

np.savez(os.path.join(BASE, "features.npz"), rms=rms, low=low, mid=mid, high=high,
         centroid=centroid, flux=flux_n, transient=transient, silence=silence, fps=FPS)
summary = {
    "duration_s": round(dur, 2), "feature_fps": FPS, "n_frames": int(nfrm),
    "transient_count": int(transient.sum()),
    "transient_rate_per_s": round(float(transient.sum()) / dur, 2),
    "silence_ratio": round(float(silence.mean()), 3),
    "centroid_mean_hz": round(float(centroid.mean()), 1),
    "centroid_p10_p90": [round(float(np.percentile(centroid, p)), 1) for p in (10, 90)],
    "band_energy_ratio_low_mid_high": [round(float(b.sum() / mag.sum()), 3) for b in (low, mid, high)],
    "repetition_period_frames": period, "repetition_period_s": round(period / FPS, 3),
}
with open(os.path.join(BASE, "features.json"), "w") as f:
    json.dump(summary, f, indent=1)
print(json.dumps(summary, indent=1))

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = np.arange(nfrm) / FPS
    fig, axs = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
    axs[0].plot(t, rms); axs[0].set_ylabel("RMS")
    for s, e in [(0, 0)]: pass
    axs[0].fill_between(t, 0, rms.max(), where=silence, alpha=0.2, color='gray', label='silence')
    axs[0].legend()
    axs[1].plot(t, low, label='low'); axs[1].plot(t, mid, label='mid'); axs[1].plot(t, high, label='high')
    axs[1].legend(); axs[1].set_ylabel("band energy")
    axs[2].plot(t, flux_n); axs[2].vlines(t[transient], 0, 1, color='r', alpha=0.4)
    axs[2].set_ylabel("flux/transients")
    axs[3].plot(t, centroid); axs[3].set_ylabel("centroid Hz"); axs[3].set_xlabel("s")
    fig.suptitle("sound.wav features (Komet - plus)")
    fig.tight_layout()
    fig.savefig(os.path.join(BASE, "feature_panel.png"), dpi=110)
    print("panel saved")
except Exception as e:
    print("plot skipped:", e)
