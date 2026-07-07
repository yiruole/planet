#!/usr/bin/env python3
"""Phase 3: manual Blender blocking reconstruction of the studio corner from
5.bottle_magic_reveal_scan.mp4 (pink stool + turpentine bottle + canvases +
radiator vent). Headless: blender -b --python build_space_block.py -- <outdir> [still|anim]"""
import bpy, sys, math

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
MODE = argv[1] if len(argv) > 1 else "still"

# --- reset scene ---
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.fps = 30
for attr in ('use_raytracing', 'use_ssr', 'use_ssr_refraction'):
    if hasattr(sc.eevee, attr): setattr(sc.eevee, attr, True)

def mat(name, color, rough=0.6, metal=0.0, transmission=0.0, ior=1.45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    for key in ('Transmission Weight', 'Transmission'):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = transmission
            break
    bsdf.inputs['IOR'].default_value = ior
    if transmission > 0:
        for attr in ('use_raytrace_refraction', 'use_screen_refraction'):
            if hasattr(m, attr): setattr(m, attr, True)
    return m

def add_cyl(name, r, h, loc, m, verts=32, scale=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc)
    o = bpy.context.object; o.name = name; o.data.materials.append(m)
    if scale: o.scale = scale
    for p in o.data.polygons: p.use_smooth = True
    return o

def add_box(name, size, loc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=2, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(m)
    return o

# --- materials ---
m_floor = mat('floor', (0.82, 0.80, 0.75), 0.5)
m_wall = mat('wall', (0.88, 0.88, 0.87), 0.8)
m_pink = mat('pink', (0.80, 0.48, 0.58), 0.35)
m_white = mat('canvas', (0.92, 0.92, 0.90), 0.7)
m_red = mat('red', (0.55, 0.10, 0.10), 0.6)
m_ink = mat('ink', (0.75, 0.74, 0.68), 0.7)
m_glass = mat('glass', (0.95, 0.97, 0.97), 0.05, transmission=1.0, ior=1.45)
m_cap = mat('cap', (0.95, 0.95, 0.95), 0.4)
m_label = mat('label', (0.20, 0.20, 0.20), 0.55)
m_vent = mat('vent', (0.80, 0.81, 0.83), 0.45)
m_dark = mat('dark', (0.08, 0.08, 0.08), 0.4)

# --- room ---
add_box('floor', (6, 6, 0.02), (0, 0, -0.01), m_floor)
add_box('wall_back', (6, 0.05, 3), (0, 1.15, 1.5), m_wall)
add_box('wall_left', (0.05, 6, 3), (-2.2, 0, 1.5), m_wall)

# --- pink stool (seat + lip + 4 splayed legs) ---
add_cyl('seat', 0.165, 0.05, (0, 0, 0.435), m_pink, 48)
add_cyl('seat_lip', 0.155, 0.06, (0, 0, 0.40), m_pink, 48)
for i in range(4):
    a = math.radians(45 + 90 * i)
    top = (0.13 * math.cos(a), 0.13 * math.sin(a), 0.40)
    bot = (0.19 * math.cos(a), 0.19 * math.sin(a), 0.0)
    mid = ((top[0] + bot[0]) / 2, (top[1] + bot[1]) / 2, 0.20)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.016, depth=0.42, location=mid)
    leg = bpy.context.object; leg.name = f'leg{i}'; leg.data.materials.append(m_pink)
    dx, dy = bot[0] - top[0], bot[1] - top[1]
    leg.rotation_euler = (math.atan2(math.hypot(dx, dy), 0.40) * -1 if False else math.atan2(math.hypot(dx, dy), 0.40), 0, math.atan2(dy, dx) - math.pi / 2)

# --- bottle (body + shoulder + cap + label wrap) ---
add_cyl('bottle_body', 0.042, 0.17, (0, 0, 0.55), m_glass, 32)
bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.042, radius2=0.017, depth=0.05, location=(0, 0, 0.66))
sh = bpy.context.object; sh.name = 'shoulder'; sh.data.materials.append(m_glass)
for p in sh.data.polygons: p.use_smooth = True
add_cyl('neck', 0.017, 0.025, (0, 0, 0.697), m_glass, 24)
add_cyl('cap', 0.019, 0.028, (0, 0, 0.722), m_cap, 24)
add_cyl('label', 0.0425, 0.075, (0, 0, 0.56), m_label, 32)

# --- canvases leaning on back wall ---
add_box('canvas1', (0.55, 0.02, 0.75), (1.05, 1.05, 0.38), m_white, rot=(math.radians(-8), 0, 0))
add_box('canvas2', (0.5, 0.02, 0.68), (0.95, 0.98, 0.34), m_white, rot=(math.radians(-12), 0, math.radians(6)))
add_box('board_red', (0.45, 0.02, 0.55), (-0.75, 1.02, 0.28), m_red, rot=(math.radians(-10), 0, 0))
add_box('board_ink', (0.42, 0.02, 0.52), (-0.55, 0.95, 0.26), m_ink, rot=(math.radians(-14), 0, math.radians(-4)))

# --- radiator vent panel (frame + horizontal slats) ---
add_box('vent_frame', (1.5, 0.06, 1.05), (-0.35, 1.12, 1.15), m_vent)
for i in range(13):
    add_box(f'slat{i}', (1.38, 0.08, 0.045), (-0.35, 1.10, 0.72 + i * 0.072), m_dark)

# --- tripod leg hint (from ref b) ---
add_cyl('tripod', 0.012, 1.1, (-1.35, 0.55, 0.55), m_dark, 12)
bpy.context.object.rotation_euler = (math.radians(20), 0, 0)

# --- light ---
bpy.ops.object.light_add(type='AREA', location=(1.6, -1.2, 2.4))
L = bpy.context.object; L.data.energy = 420; L.data.size = 2.4
L.rotation_euler = (math.radians(35), math.radians(18), math.radians(15))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs[0].default_value = (0.9, 0.9, 0.92, 1); bg.inputs[1].default_value = 0.55

# --- camera orbit: low front view -> elevated 3/4 view ---
bpy.ops.object.empty_add(location=(0, 0, 0.5)); tgt = bpy.context.object; tgt.name = 'target'
bpy.ops.object.camera_add(location=(-0.45, -1.45, 0.75))
cam = bpy.context.object; sc.camera = cam
cam.data.lens = 32
tr = cam.constraints.new('TRACK_TO'); tr.target = tgt
tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'

sc.frame_start, sc.frame_end = 1, 180
for f, pos, tz in [(1, (-0.45, -1.45, 0.75), 0.50), (90, (0.15, -1.55, 1.0), 0.48), (180, (0.55, -1.15, 1.45), 0.42)]:
    cam.location = pos
    cam.keyframe_insert('location', frame=f)
    tgt.location = (0, 0, tz)
    tgt.keyframe_insert('location', frame=f)

sc.render.image_settings.file_format = 'JPEG'
if MODE == 'still':
    for f in (1, 120):
        sc.frame_set(f)
        sc.render.filepath = f"{OUT}/still_f{f:03d}.jpg"
        bpy.ops.render.render(write_still=True)
else:
    sc.render.filepath = f"{OUT}/anim/f"
    bpy.ops.render.render(animation=True)
print("BLOCK DONE", MODE)
