#!/usr/bin/env python3
"""Phase 4: sound-driven studio space. Reuses Phase-3 blocking scene; drives
3 mapped variables from features.npz (bass->key light breath, transients->
bottle knock impulses, centroid->camera approach). Silence = rest state.
Run: blender -b --python build_sound_space.py -- <outdir> driven|static"""
import bpy, sys, os, math
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
MODE = argv[1] if len(argv) > 1 else "driven"

P3 = os.path.expanduser("~/Desktop/Digital Art/test/results/phase3")
P4 = os.path.expanduser("~/Desktop/Digital Art/test/results/phase4")

# build the Phase-3 scene by executing its script body up to (not incl.) camera/render
src = open(os.path.join(P3, "build_space_block.py")).read()
body = src.split("# --- camera orbit")[0]
body = body.replace('argv = sys.argv[sys.argv.index("--") + 1:]\nOUT = argv[0]\nMODE = argv[1] if len(argv) > 1 else "still"\n', '')
exec(compile(body, "phase3_scene", "exec"), {"bpy": bpy, "sys": sys, "math": math})
sc = bpy.context.scene

# --- features ---
F = np.load(os.path.join(P4, "features.npz"))
OFFSET = 60          # start at 2.0s into track
N = 450              # 15s @ 30fps
bass = F["low"][OFFSET:OFFSET + N]
bass_n = np.convolve(bass / (np.percentile(bass, 98) + 1e-9), np.ones(3) / 3, 'same').clip(0, 1)
trans = F["transient"][OFFSET:OFFSET + N].astype(np.float32)
# knock curve: impulse -> exp decay over ~8 frames, alternating sign
kern = np.exp(-np.arange(10) / 3.0)
signs = np.ones_like(trans)
idx = np.where(trans > 0)[0]
for j, i in enumerate(idx):
    signs[i] = 1 if j % 2 == 0 else -1
knock = np.convolve(trans * signs, kern, 'full')[:N]
cent = F["centroid"][OFFSET:OFFSET + N]
cent_n = np.convolve((cent - 400) / 2200.0, np.ones(15) / 15, 'same').clip(0, 1)

if MODE == "static":
    bass_n = np.zeros(N); knock = np.zeros(N); cent_n = np.zeros(N)

# --- objects to drive ---
key = next(o for o in sc.objects if o.type == 'LIGHT')
bottle_parts = [sc.objects[n] for n in ('bottle_body', 'shoulder', 'neck', 'cap', 'label')]
bpy.ops.object.empty_add(location=(0, 0, 0.47))
pivot = bpy.context.object; pivot.name = 'bottle_pivot'
for o in bottle_parts:
    o.parent = pivot; o.matrix_parent_inverse = pivot.matrix_world.inverted()

bpy.ops.object.empty_add(location=(0, 0, 0.5)); tgt = bpy.context.object
bpy.ops.object.camera_add(location=(-0.45, -1.45, 0.75))
cam = bpy.context.object; sc.camera = cam; cam.data.lens = 32
tr = cam.constraints.new('TRACK_TO'); tr.target = tgt
tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'

home = np.array([-0.45, -1.45, 0.75])
near = np.array([-0.15, -1.05, 0.62])

sc.frame_start, sc.frame_end = 1, N
warm = np.array([1.0, 0.72, 0.45]); base_col = np.array([1.0, 0.95, 0.90])
for f in range(N):
    fr = f + 1
    b, k, c = float(bass_n[f]), float(knock[f]), float(cent_n[f])
    key.data.energy = 130 + 640 * b
    col = base_col * (1 - 0.55 * b) + warm * (0.55 * b)
    key.data.color = tuple(col)
    key.data.keyframe_insert('energy', frame=fr)
    key.data.keyframe_insert('color', frame=fr)
    pivot.rotation_euler = (0.04 * k, 0.02 * k, 0.30 * k)
    pivot.location = (0, 0, 0.47 + 0.006 * abs(k))
    pivot.keyframe_insert('rotation_euler', frame=fr)
    pivot.keyframe_insert('location', frame=fr)
    cam.location = tuple(home * (1 - 0.5 * c) + near * (0.5 * c))
    cam.keyframe_insert('location', frame=fr)

sc.render.image_settings.file_format = 'JPEG'
if MODE == "static":
    for fr in (1, 100, 208, 300):
        sc.frame_set(fr)
        sc.render.filepath = f"{OUT}/static_f{fr:04d}.jpg"
        bpy.ops.render.render(write_still=True)
else:
    os.makedirs(f"{OUT}/anim", exist_ok=True)
    sc.render.filepath = f"{OUT}/anim/f"
    bpy.ops.render.render(animation=True)
print("SOUND SPACE DONE", MODE)
