#!/usr/bin/env python3
"""motion_trace — motion-difference-driven temporal transformation.

Moving regions leave decaying luminous traces; static regions stay clean.
Not an overlay: the trace buffer is driven by per-pixel temporal difference,
so the effect is structurally coupled to motion in the footage.

Pipeline: ffmpeg rawvideo decode → numpy (luma diff → soft motion mask →
decaying trace buffer → composite) → ffmpeg h264 encode.
Deps: ffmpeg + numpy only. Originals never modified.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np


def probe(src):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_streams", "-select_streams", "v:0", src],
        capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffprobe failed: {r.stderr[:200]}")
    s = json.loads(r.stdout)["streams"][0]
    num, _, den = (s.get("avg_frame_rate") or "24/1").partition("/")
    fps = float(num) / float(den or 1)
    return int(s["width"]), int(s["height"]), fps


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("video")
    ap.add_argument("-o", "--output", default=None)
    ap.add_argument("--mode", choices=["trace", "echo"], default="trace",
                    help="trace: luminous decaying trails; "
                         "echo: ghost frames of past motion")
    ap.add_argument("--decay", type=float, default=0.92,
                    help="per-frame trace decay 0-1 (higher = longer trails)")
    ap.add_argument("--threshold", type=float, default=14.0,
                    help="luma diff (0-255) where motion mask starts")
    ap.add_argument("--softness", type=float, default=24.0,
                    help="diff range over which mask ramps 0→1")
    ap.add_argument("--strength", type=float, default=1.0,
                    help="trace intensity multiplier")
    args = ap.parse_args()

    src = os.path.abspath(args.video)
    if not os.path.exists(src):
        sys.exit(f"not found: {src}")
    out = args.output or (
        os.path.splitext(src)[0] + f"_{args.mode}.mp4")
    if os.path.abspath(out) == src:
        sys.exit("refusing to overwrite source")

    w, h, fps = probe(src)
    fsize = w * h * 3

    dec = subprocess.Popen(
        ["ffmpeg", "-v", "quiet", "-i", src,
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE)
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "quiet", "-y",
         "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{w}x{h}", "-r", f"{fps}", "-i", "-",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out],
        stdin=subprocess.PIPE)

    prev_luma = None
    trace = np.zeros((h, w, 3), dtype=np.float32)
    n = 0
    while True:
        buf = dec.stdout.read(fsize)
        if len(buf) < fsize:
            break
        frame = np.frombuffer(buf, np.uint8).reshape(h, w, 3).astype(np.float32)
        luma = frame @ np.array([0.299, 0.587, 0.114], np.float32)

        if prev_luma is None:
            mask = np.zeros((h, w), np.float32)
        else:
            diff = np.abs(luma - prev_luma)
            mask = np.clip((diff - args.threshold) / max(args.softness, 1e-3),
                           0.0, 1.0)
        prev_luma = luma

        m3 = mask[..., None] * args.strength
        if args.mode == "trace":
            # moving pixels refresh the trace at full brightness, then decay
            trace = np.maximum(trace * args.decay, frame * m3)
            comp = np.maximum(frame, trace)
        else:  # echo: past moving regions ghost over the present
            trace = trace * args.decay + frame * m3 * (1.0 - args.decay)
            comp = np.clip(frame + trace * 1.8, 0, 255)

        enc.stdin.write(comp.astype(np.uint8).tobytes())
        n += 1

    dec.stdout.close()
    enc.stdin.close()
    enc.wait()
    print(json.dumps({"output": out, "frames": n,
                      "resolution": f"{w}x{h}", "fps": fps,
                      "mode": args.mode, "decay": args.decay,
                      "threshold": args.threshold}))


if __name__ == "__main__":
    main()
