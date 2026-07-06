#!/usr/bin/env python3
"""media_inspect — structural video analysis with ffmpeg only (no heavy deps).

Outputs into <video>_analysis/ (or --outdir):
  metadata.json      ffprobe streams + format
  shots.json         scene-change timestamps (ffmpeg scene filter)
  contact_sheet.jpg  uniform-sampled grid covering full duration
  frames/            one representative PNG per detected shot (mid-shot)

Originals are never modified (see creative-rules/media-rules.md).
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def ffprobe_metadata(src):
    r = run([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", src,
    ])
    if r.returncode != 0:
        sys.exit(f"ffprobe failed: {r.stderr.strip()[:300]}")
    return json.loads(r.stdout)


def video_stream(meta):
    for s in meta.get("streams", []):
        if s.get("codec_type") == "video":
            return s
    sys.exit("no video stream found")


def parse_fps(s):
    num, _, den = (s or "0/1").partition("/")
    try:
        return float(num) / float(den or 1)
    except ZeroDivisionError:
        return 0.0


def detect_shots(src, threshold):
    """Return sorted list of scene-change timestamps (seconds)."""
    r = run([
        "ffmpeg", "-i", src,
        "-vf", f"select='gt(scene,{threshold})',metadata=print",
        "-an", "-f", "null", "-",
    ])
    times = []
    for line in r.stderr.splitlines():
        m = re.search(r"pts_time:([0-9.]+)", line)
        if m:
            times.append(round(float(m.group(1)), 3))
    return sorted(set(times))


def has_filter(name):
    r = run(["ffmpeg", "-hide_banner", "-filters"])
    return re.search(rf"\s{name}\s", r.stdout) is not None


def contact_sheet(src, duration, out_path, grid):
    """Returns (ok, sample_times). Timestamps burned in only if drawtext exists."""
    cols, rows = grid
    n = cols * rows
    # uniform sampling: one frame every duration/n seconds
    interval = max(duration / n, 0.001)
    sample_times = [round(i * interval, 2) for i in range(n)]
    stamp = (
        f"drawtext=text='%{{pts\\:hms}}':fontsize=20:fontcolor=white:"
        f"box=1:boxcolor=black@0.5:x=8:y=8,"
    ) if has_filter("drawtext") else ""
    vf = f"fps=1/{interval:.6f},{stamp}scale=480:-1,tile={cols}x{rows}"
    r = run([
        "ffmpeg", "-y", "-i", src, "-vf", vf,
        "-frames:v", "1", "-q:v", "3", out_path,
    ])
    return r.returncode == 0, sample_times


def extract_shot_frames(src, duration, shot_times, frames_dir):
    """One representative frame per shot (midpoint), PNG at source res."""
    os.makedirs(frames_dir, exist_ok=True)
    bounds = [0.0] + shot_times + [duration]
    saved = []
    for i in range(len(bounds) - 1):
        start, end = bounds[i], bounds[i + 1]
        if end - start < 0.05:
            continue
        mid = (start + end) / 2
        name = f"shot{i:03d}_t{mid:07.2f}.png"
        out = os.path.join(frames_dir, name)
        r = run(["ffmpeg", "-y", "-ss", f"{mid:.3f}", "-i", src,
                 "-frames:v", "1", out])
        if r.returncode == 0 and os.path.exists(out):
            saved.append({"shot": i, "start": start, "end": end,
                          "frame_time": round(mid, 3), "file": name})
    return saved


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("video")
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--scene-threshold", type=float, default=0.3)
    ap.add_argument("--grid", default="4x4", help="contact sheet cols x rows")
    args = ap.parse_args()

    src = os.path.abspath(args.video)
    if not os.path.exists(src):
        sys.exit(f"not found: {src}")
    outdir = args.outdir or os.path.splitext(src)[0] + "_analysis"
    os.makedirs(outdir, exist_ok=True)
    cols, rows = (int(x) for x in args.grid.lower().split("x"))

    meta = ffprobe_metadata(src)
    vs = video_stream(meta)
    duration = float(meta.get("format", {}).get("duration") or 0)
    summary = {
        "source": src,
        "duration_s": round(duration, 3),
        "resolution": f"{vs.get('width')}x{vs.get('height')}",
        "fps": round(parse_fps(vs.get("avg_frame_rate")), 3),
        "codec": vs.get("codec_name"),
        "bitrate_kbps": int(meta.get("format", {}).get("bit_rate") or 0) // 1000,
        "audio": any(s.get("codec_type") == "audio" for s in meta["streams"]),
    }
    with open(os.path.join(outdir, "metadata.json"), "w") as f:
        json.dump({"summary": summary, "ffprobe": meta}, f, indent=2)

    shots = detect_shots(src, args.scene_threshold)
    frames = extract_shot_frames(src, duration, shots,
                                 os.path.join(outdir, "frames"))
    with open(os.path.join(outdir, "shots.json"), "w") as f:
        json.dump({"scene_threshold": args.scene_threshold,
                   "cut_times": shots, "shot_frames": frames}, f, indent=2)

    sheet = os.path.join(outdir, "contact_sheet.jpg")
    sheet_ok, sample_times = contact_sheet(src, duration, sheet, (cols, rows))

    print(json.dumps({
        "outdir": outdir,
        "summary": summary,
        "n_cuts": len(shots),
        "n_shot_frames": len(frames),
        "contact_sheet": sheet if sheet_ok else None,
        "sheet_grid": f"{cols}x{rows} 逐行左到右",
        "sheet_sample_times_s": sample_times if sheet_ok else None,
    }, indent=2))


if __name__ == "__main__":
    main()
