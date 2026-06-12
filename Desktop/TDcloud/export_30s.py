# Export 30s MP4 with audio — runs inside TouchDesigner via td_execfile

import time, os

FPS        = 60
DURATION_S = 30
OUT_PATH   = '/Users/ruoleyi/Desktop/TDcloud_export_30s.mp4'

# ── Get or create Movie File Out TOP ────────────────────────────────────
mfo = op('/project1/cloud_movieout')
if not mfo:
    mfo = op('/project1').create(moviefileoutTOP, 'cloud_movieout')
    mfo.nodeX, mfo.nodeY = 600, -200

# ── Wire video: prefer cloud_out, fallback to cloud_glsl ────────────────
vid = op('/project1/cloud_out') or op('/project1/cloud_glsl')
if vid:
    mfo.inputConnectors[0].connect(vid)
    print(f"Video source: {vid.path}")
else:
    print("WARNING: no video source found")

# ── Wire audio from audiofilein1 ─────────────────────────────────────────
aud = op('/project1/audiofilein1')
if aud:
    try:
        mfo.inputConnectors[1].connect(aud)
        print(f"Audio source: {aud.path}")
    except Exception as e:
        print(f"Audio wire skipped ({e}) — will export video only")

# ── Configure output ─────────────────────────────────────────────────────
mfo.par.file        = OUT_PATH
mfo.par.record      = False   # make sure it's off before we start

# resolution matches cloud_glsl
try:
    mfo.par.resolutionw = 1280
    mfo.par.resolutionh = 720
except: pass

# ── Start recording ──────────────────────────────────────────────────────
mfo.par.record = True
frames = int(FPS * DURATION_S)
print(f"Recording started → {OUT_PATH}")
print(f"Stopping in {DURATION_S}s ({frames} frames @ {FPS}fps)…")

# ── Schedule auto-stop ───────────────────────────────────────────────────
run("""
mfo = op('/project1/cloud_movieout')
mfo.par.record = False
print("Recording stopped.")
print("Saved: /Users/ruoleyi/Desktop/TDcloud_export_30s.mp4")
""", delayFrames=frames)
