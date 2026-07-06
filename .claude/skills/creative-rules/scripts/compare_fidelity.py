#!/usr/bin/env python3
"""compare_fidelity — evidence panel for reference-vs-ours fidelity iteration.

NOT a similarity scorer. Renders the dimensions human eyes gloss over
(luminance distribution, edge/detail density, event timing) as visible
evidence; judgment stays with the reader. See creative-rules/fidelity-rules.md.

Image mode : compare_fidelity.py ref.png ours.png [-o panel.png]
Video mode : compare_fidelity.py ref.mp4 ours.mp4 [-o panel.png]
Needs numpy + matplotlib (anaconda python has both) + ffmpeg for video.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}


def luma(a):
    return a @ np.array([0.299, 0.587, 0.114], np.float32)


def edges(l):
    gx = np.abs(np.gradient(l, axis=1))
    gy = np.abs(np.gradient(l, axis=0))
    return np.hypot(gx, gy)


def block_mean(e, n=6):
    h, w = e.shape
    bh, bw = h // n, w // n
    return np.array([[e[i*bh:(i+1)*bh, j*bw:(j+1)*bw].mean()
                      for j in range(n)] for i in range(n)])


def load_image(p):
    from PIL import Image
    return np.asarray(Image.open(p).convert("RGB"), np.float32)


def image_stats(a):
    l = luma(a)
    mx, mn = a.max(-1), a.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1)
    return {
        "luma_mean": round(float(l.mean()), 1),
        "dark_frac_lt40": round(float((l < 40).mean()), 4),
        "bright_frac_gt200": round(float((l > 200).mean()), 4),
        "edge_mean": round(float(edges(l).mean()), 3),
        "saturation_mean": round(float(sat.mean()), 3),
    }


def image_mode(ref_p, out_p, panel_p):
    ref, out = load_image(ref_p), load_image(out_p)
    lr, lo = luma(ref), luma(out)
    er, eo = edges(lr), edges(lo)
    ratio = block_mean(eo) / np.maximum(block_mean(er), 1e-3)

    fig, ax = plt.subplots(2, 3, figsize=(15, 9))
    ax[0, 0].imshow(ref.astype(np.uint8)); ax[0, 0].set_title("REF")
    ax[0, 1].imshow(out.astype(np.uint8)); ax[0, 1].set_title("OURS")
    ax[0, 2].hist(lr.ravel(), 64, alpha=0.6, label="ref", density=True)
    ax[0, 2].hist(lo.ravel(), 64, alpha=0.6, label="ours", density=True)
    ax[0, 2].legend(); ax[0, 2].set_title("luminance distribution")
    vmax = np.percentile(er, 99)
    ax[1, 0].imshow(er, cmap="inferno", vmax=vmax)
    ax[1, 0].set_title(f"REF edges (mean {er.mean():.2f})")
    ax[1, 1].imshow(eo, cmap="inferno", vmax=vmax)
    ax[1, 1].set_title(f"OURS edges (mean {eo.mean():.2f})")
    im = ax[1, 2].imshow(ratio, cmap="RdBu_r", vmin=0, vmax=2)
    ax[1, 2].set_title("edge density ours/ref\nred: busier, blue: emptier")
    plt.colorbar(im, ax=ax[1, 2])
    for a in ax.flat:
        if a is not ax[0, 2]:
            a.set_xticks([]); a.set_yticks([])
    plt.tight_layout(); plt.savefig(panel_p, dpi=80); plt.close()

    order = np.dstack(np.unravel_index(np.argsort(ratio.ravel()), ratio.shape))[0]
    print(json.dumps({
        "mode": "image", "panel": panel_p,
        "ref": image_stats(ref), "ours": image_stats(out),
        "emptiest_blocks_rowcol": [list(map(int, x)) for x in order[:3]],
        "busiest_blocks_rowcol": [list(map(int, x)) for x in order[-3:]],
    }, indent=2))


# ---------------- video mode ----------------

def luma_curve(path, fps=10, size=96):
    """Mean luma per sampled frame via ffmpeg rawvideo pipe."""
    p = subprocess.Popen(
        ["ffmpeg", "-v", "quiet", "-i", path, "-vf",
         f"fps={fps},scale={size}:{size}", "-f", "rawvideo",
         "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    vals = []
    fsize = size * size
    while True:
        buf = p.stdout.read(fsize)
        if len(buf) < fsize:
            break
        vals.append(np.frombuffer(buf, np.uint8).mean())
    return np.array(vals, np.float32), fps


def events(curve, fps, jump=8.0):
    """Times where mean luma jumps sharply between samples."""
    d = np.diff(curve)
    idx = np.where(np.abs(d) > jump)[0]
    # merge consecutive indices into event starts
    ev = []
    for i in idx:
        if not ev or i - ev[-1][0] > 2:
            ev.append([i, d[i]])
    return [(round(i / fps, 2), round(float(v), 1)) for i, v in ev]


def video_mode(ref_p, out_p, panel_p):
    cr, fps = luma_curve(ref_p)
    co, _ = luma_curve(out_p)
    tr = np.arange(len(cr)) / fps
    to = np.arange(len(co)) / fps
    er, eo = events(cr, fps), events(co, fps)

    fig, ax = plt.subplots(1, 1, figsize=(14, 5))
    ax.plot(tr, cr, label=f"ref ({len(cr)/fps:.1f}s)", lw=2)
    ax.plot(to, co, label=f"ours ({len(co)/fps:.1f}s)", lw=2)
    for t, v in er:
        ax.axvline(t, color="tab:blue", alpha=0.35, ls="--")
    for t, v in eo:
        ax.axvline(t, color="tab:orange", alpha=0.35, ls=":")
    ax.set_xlabel("time (s)"); ax.set_ylabel("mean luma")
    ax.set_title("temporal luminance profile — event timing / duration / rhythm")
    ax.legend()
    plt.tight_layout(); plt.savefig(panel_p, dpi=80); plt.close()

    print(json.dumps({
        "mode": "video", "panel": panel_p,
        "ref": {"duration_s": round(len(cr) / fps, 2),
                "events_t_jump": er,
                "luma_mean": round(float(cr.mean()), 1)},
        "ours": {"duration_s": round(len(co) / fps, 2),
                 "events_t_jump": eo,
                 "luma_mean": round(float(co.mean()), 1)},
        "note": "event = mean-luma jump >8/sample; compare timing, count, sign",
    }, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ref"); ap.add_argument("ours")
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()
    is_video = os.path.splitext(args.ref)[1].lower() in VIDEO_EXT
    panel = args.output or (os.path.splitext(args.ours)[0] +
                            ("_fidelity_video.png" if is_video else "_fidelity.png"))
    (video_mode if is_video else image_mode)(args.ref, args.ours, panel)


if __name__ == "__main__":
    main()
