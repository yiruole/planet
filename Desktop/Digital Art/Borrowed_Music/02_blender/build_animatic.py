#!/usr/bin/env python3
"""Borrowed Music — STAGE 2 greybox animatic. One .blend, two sets (EXT origin,
INT at x+100), 6 shots via timeline-marker camera binding, 708f @24fps 640x360.
Run: blender -b --python build_animatic.py -- <outdir> still|anim"""
import bpy, sys, os, math

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
MODE = argv[1] if len(argv) > 1 else "still"

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x, sc.render.resolution_y = 640, 360
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, 708

def mat(name, color, rough=0.7, emit=0.0, emit_col=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    if emit > 0 and 'Emission Strength' in b.inputs:
        b.inputs['Emission Color'].default_value = (*(emit_col or color), 1)
        b.inputs['Emission Strength'].default_value = emit
    return m

def box(name, size, loc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=2, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    o.scale = (size[0]/2, size[1]/2, size[2]/2)
    o.data.materials.append(m)
    return o

def cyl(name, r, h, loc, m, rot=(0, 0, 0), v=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth = True
    return o

def sph(name, r, loc, m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=r, location=loc)
    o = bpy.context.object; o.name = name; o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth = True
    return o

def bsdf_of(o):
    return next(n for n in o.data.materials[0].node_tree.nodes if n.type == 'BSDF_PRINCIPLED')

# ================= materials =================
m_ground = mat('ground', (0.030, 0.028, 0.026), 0.95)
m_hab = mat('habitat', (0.10, 0.10, 0.11), 0.6)
m_win = mat('hab_window', (0.9, 0.75, 0.5), 0.4, emit=3.0, emit_col=(1.0, 0.8, 0.55))
m_rover = mat('rover', (0.06, 0.06, 0.065), 0.7)
m_suit = mat('suit', (0.30, 0.30, 0.32), 0.6)
m_room = mat('room', (0.055, 0.058, 0.065), 0.85)
m_ward = mat('wardrobe', (0.09, 0.085, 0.08), 0.7)
m_rail = mat('rail', (0.25, 0.25, 0.25), 0.35)
m_shadowobj = mat('anomaly', (0.012, 0.012, 0.014), 0.9)

# ================= EXT set (origin) =================
box('ground', (300, 300, 0.05), (0, 0, -0.025), m_ground)
hab = sph('habitat_dome', 3.2, (0, 0, 0.4), m_hab); hab.scale = (1, 1, 0.62)
box('airlock', (1.4, 0.9, 1.9), (0, -3.0, 0.95), m_hab)
box('hab_win', (1.8, 0.05, 0.28), (0.4, -2.95, 1.35), m_win)
rv = box('rover_body', (1.6, 1.0, 0.5), (-8.5, 2.0, 0.75), m_rover)
for i, (wx, wy) in enumerate([(-0.6, -0.55), (0, -0.55), (0.6, -0.55), (-0.6, 0.55), (0, 0.55), (0.6, 0.55)]):
    cyl(f'wheel{i}', 0.28, 0.2, (-8.5 + wx, 2.0 + wy, 0.28), m_rover, rot=(math.pi/2, 0, 0))
cyl('mast', 0.05, 0.9, (-8.1, 2.0, 1.45), m_rover)
box('mast_head', (0.3, 0.12, 0.12), (-8.1, 2.0, 1.95), m_rover)

def astronaut(prefix, loc):
    g = {}
    g['body'] = cyl(prefix + '_body', 0.24, 1.05, (loc[0], loc[1], 0.78), m_suit)
    g['head'] = sph(prefix + '_head', 0.17, (loc[0], loc[1], 1.52), m_suit)
    g['pack'] = box(prefix + '_pack', (0.36, 0.18, 0.5), (loc[0], loc[1] - 0.24, 1.05), m_suit)
    m_patch = mat(prefix + '_patch', (0.05, 0.05, 0.06), 0.5, emit=0.0, emit_col=(0.55, 0.6, 0.75))
    g['patch'] = box(prefix + '_patchobj', (0.2, 0.02, 0.3), (loc[0], loc[1] + 0.25, 1.05), m_patch)
    for o in g.values():
        o.parent = g['body'] if o is not g['body'] else None
    for k in ('head', 'pack', 'patch'):
        g[k].parent = g['body']
        g[k].matrix_parent_inverse = g['body'].matrix_world.inverted()
    return g

ext_ast = astronaut('ext', (0.8, -3.6, 0))
# hidden underground until S05 (frame 505)
b = ext_ast['body']
b.location = (0.8, -3.6, -6.0); b.keyframe_insert('location', frame=504)
b.location = (0.8, -3.6, 0.78); b.keyframe_insert('location', frame=505)
b.location = (6.5, -9.5, 0.78); b.keyframe_insert('location', frame=640)
b.keyframe_insert('location', frame=708)
# (1-frame underground->surface pop; Blender 5.1 removed Action.fcurves so no
#  interpolation surgery — adjacent keyframes make the transition invisible)
# ext patch faint on from 505, dip at missing-note 682
pb = bsdf_of(ext_ast['patch']).inputs['Emission Strength']
for f, v in [(504, 0.0), (552, 0.0), (566, 0.5), (680, 0.5), (683, 0.12), (690, 0.45)]:
    pb.default_value = v; pb.keyframe_insert('default_value', frame=f)

# anomaly shadow object (S06, far, barely visible)
an = box('anomaly', (3.2, 0.25, 1.5), (26, 14, 0.9), m_shadowobj)
an.location = (26, 14, 0.9); an.keyframe_insert('location', frame=660)
an.location = (22, 17, 0.9); an.keyframe_insert('location', frame=706)

# moon/star light
bpy.ops.object.light_add(type='SUN')
sun = bpy.context.object
sun.rotation_euler = (math.radians(70), 0, math.radians(-30))
sun.data.energy = 0.45; sun.data.color = (0.72, 0.80, 1.0); sun.data.angle = 0.05
# missing-note dip (frame 682) — subtle world response
sun.data.keyframe_insert('energy', frame=678)
sun.data.energy = 0.34; sun.data.keyframe_insert('energy', frame=682)
sun.data.energy = 0.45; sun.data.keyframe_insert('energy', frame=688)

# rover vibrates once at frame 610
rv.rotation_euler = (0, 0, 0); rv.keyframe_insert('rotation_euler', frame=608)
rv.rotation_euler = (0, 0.010, 0); rv.keyframe_insert('rotation_euler', frame=610)
rv.rotation_euler = (0, -0.006, 0); rv.keyframe_insert('rotation_euler', frame=612)
rv.rotation_euler = (0, 0, 0); rv.keyframe_insert('rotation_euler', frame=615)

# starfield world
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
nt = w.node_tree
bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 140.0
lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = 0.028
mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 6.0
nt.links.new(vor.outputs['Distance'], lt.inputs[0])
nt.links.new(lt.outputs[0], mul.inputs[0])
nt.links.new(mul.outputs[0], bg.inputs['Strength'])
bg.inputs[0].default_value = (0.85, 0.88, 1.0, 1)

# ================= INT set (x + 100) =================
X = 100.0
box('floor_i', (8, 8, 0.05), (X, 0, -0.025), m_room)
box('ceil_i', (8, 8, 0.05), (X, 0, 2.62), m_room)
box('wall_back_i', (8, 0.05, 2.6), (X, 2.0, 1.3), m_room)
box('wall_l_i', (0.05, 8, 2.6), (X - 3.0, 0, 1.3), m_room)
box('wall_r_i', (0.05, 8, 2.6), (X + 3.0, 0, 1.3), m_room)
# wardrobe shell against back wall
box('ward_back', (2.4, 0.04, 2.0), (X, 1.9, 1.15), m_ward)
box('ward_side_l', (0.04, 0.6, 2.0), (X - 1.2, 1.6, 1.15), m_ward)
box('ward_side_r', (0.04, 0.6, 2.0), (X + 1.2, 1.6, 1.15), m_ward)
box('ward_top', (2.4, 0.6, 0.04), (X, 1.6, 2.15), m_ward)
cyl('rail', 0.015, 2.3, (X, 1.55, 1.85), m_rail, rot=(0, math.pi/2, 0))
# doors hinged at outer edges, open during S02 (f117-157)
for side, hx in (('l', X - 1.2), ('r', X + 1.2)):
    bpy.ops.object.empty_add(location=(hx, 1.3, 1.15))
    hinge = bpy.context.object; hinge.name = f'hinge_{side}'
    d = box(f'door_{side}', (1.2, 0.03, 2.0), (hx + (0.6 if side == 'l' else -0.6), 1.3, 1.15), m_ward)
    d.parent = hinge; d.matrix_parent_inverse = hinge.matrix_world.inverted()
    ang = math.radians(115 if side == 'l' else -115)
    hinge.rotation_euler = (0, 0, 0); hinge.keyframe_insert('rotation_euler', frame=117)
    hinge.rotation_euler = (0, 0, ang); hinge.keyframe_insert('rotation_euler', frame=157)

# 10 music films on hangers: prototypes A membrane / B fiber / C film
films = []
proto_cols = {'A': (0.32, 0.33, 0.35), 'B': (0.16, 0.16, 0.18), 'C': (0.28, 0.24, 0.20)}
kinds = ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'V', 'B', 'C']  # index7 = dark veil hero
for i, kind in enumerate(kinds):
    fx = X - 0.95 + i * 0.21
    cyl(f'hook_{i}', 0.006, 0.09, (fx, 1.55, 1.80), m_rail, v=8)
    if kind == 'V':
        mm = mat(f'film_{i}', (0.045, 0.045, 0.05), 0.55, emit=0.15, emit_col=(0.7, 0.75, 0.9))
    else:
        c = proto_cols[kind]
        mm = mat(f'film_{i}', c, 0.5, emit=0.05, emit_col=(0.8, 0.8, 0.9))
    bpy.ops.mesh.primitive_plane_add(size=1, location=(fx, 1.53, 1.30))
    f = bpy.context.object; f.name = f'film_{i}'
    f.scale = (0.085, 1, 0.44)
    f.rotation_euler = (math.radians(90), 0, 0)
    f.data.materials.append(mm)
    films.append(f)
    # micro sway (skip hero veil #7 — its keys would fight the detach anim)
    if kind == 'V':
        continue
    for kf, a in ((97, 0.015), (250, -0.02), (400, 0.012), (560, -0.01), (708, 0.015)):
        f.rotation_euler = (math.radians(90) + a * ((i % 3) - 1), a * 0.7, 0)
        f.keyframe_insert('rotation_euler', frame=kf + i * 7)

# touch pulses on films 1,3,5,8 then veil 7 (frames 204/230/254/278/298)
for fi, fr in ((1, 204), (3, 230), (5, 254), (8, 278), (7, 298)):
    es = bsdf_of(films[fi]).inputs['Emission Strength']
    base = 0.15 if fi == 7 else 0.05
    for f, v in ((fr - 4, base), (fr, base + 0.9), (fr + 14, base)):
        es.default_value = v; es.keyframe_insert('default_value', frame=f)

# veil detach & attach to suit (S04 f440-490)
veil = films[7]
veil.keyframe_insert('location', frame=440)
veil.keyframe_insert('scale', frame=440)
veil.location = (X + 0.55, -0.35, 1.42); veil.rotation_euler = (math.radians(75), 0.25, 0.15)
veil.keyframe_insert('location', frame=470); veil.keyframe_insert('rotation_euler', frame=470)
veil.location = (X, -0.42, 1.05); veil.scale = (0.075, 1, 0.30)
veil.rotation_euler = (math.radians(90), 0.05, 0)
veil.keyframe_insert('location', frame=490); veil.keyframe_insert('scale', frame=490)
veil.keyframe_insert('rotation_euler', frame=490)

# interior astronaut (back to camera, facing wardrobe)
int_ast = astronaut('int', (X, -0.7, 0))
# arm proxy reaching to films during S03
arm = cyl('int_arm', 0.05, 0.7, (X - 0.1, 0.1, 1.30), m_suit, rot=(math.radians(75), 0, 0))
arm.keyframe_insert('location', frame=193)
for fr, fx in ((204, X - 0.74), (230, X - 0.32), (254, X + 0.10), (278, X + 0.73), (298, X + 0.52)):
    arm.location = (fx - 0.0, 0.35, 1.45)
    arm.keyframe_insert('location', frame=fr)
arm.location = (X - 0.1, 0.1, 1.30); arm.keyframe_insert('location', frame=340)
arm.keyframe_insert('location', frame=425)
arm.location = (X + 0.50, 0.30, 1.48); arm.keyframe_insert('location', frame=445)
arm.location = (X - 0.1, 0.1, 1.30); arm.keyframe_insert('location', frame=488)
# int chest patch appears when veil attaches
pi_ = bsdf_of(int_ast['patch']).inputs['Emission Strength']
for f, v in ((478, 0.0), (496, 0.4)):
    pi_.default_value = v; pi_.keyframe_insert('default_value', frame=f)

# interior light: dim cool area + tiny warm practical
bpy.ops.object.light_add(type='AREA', location=(X - 1.5, -2.0, 2.4))
Li = bpy.context.object; Li.data.energy = 28; Li.data.size = 2.2; Li.data.color = (0.75, 0.82, 0.95)
Li.rotation_euler = (math.radians(30), 0, math.radians(-15))
bpy.ops.object.light_add(type='POINT', location=(X + 1.8, 0.5, 1.9))
Lp = bpy.context.object; Lp.data.energy = 9; Lp.data.color = (1.0, 0.75, 0.5)
# wardrobe inner faint light (music leak glow) rises as doors open
bpy.ops.object.light_add(type='AREA', location=(X, 1.4, 1.5))
Lw = bpy.context.object; Lw.data.size = 2.0; Lw.data.color = (0.7, 0.75, 0.95)
Lw.rotation_euler = (math.radians(-90), 0, 0)
for f, v in ((117, 0.0), (160, 7.0)):
    Lw.data.energy = v; Lw.data.keyframe_insert('energy', frame=f)

# ================= cameras & markers =================
def camera(name, loc, tgt_loc, lens=32):
    bpy.ops.object.empty_add(location=tgt_loc)
    t = bpy.context.object; t.name = name + '_tgt'
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object; c.name = name; c.data.lens = lens
    tr = c.constraints.new('TRACK_TO'); tr.target = t
    tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    return c, t

c1, t1 = camera('cam1', (2, -40, 2.4), (0, -1, 1.1), 35)
c1.keyframe_insert('location', frame=1)
c1.location = (1, -17, 1.9); c1.keyframe_insert('location', frame=96)
c2, t2 = camera('cam2', (X + 0.2, -3.3, 1.45), (X, 1.4, 1.25), 30)
c3, t3 = camera('cam3', (X - 1.9, -1.05, 1.62), (X + 0.15, 1.55, 1.35), 30)
c3.keyframe_insert('location', frame=193); t3.keyframe_insert('location', frame=193)
c3.location = (X - 0.55, -1.05, 1.55); t3.location = (X + 0.7, 1.55, 1.30)
c3.keyframe_insert('location', frame=312); t3.keyframe_insert('location', frame=312)
c4, t4 = camera('cam4', (X - 2.85, -1.35, 1.45), (X + 0.35, 0.35, 1.15), 32)
c5, t5 = camera('cam5', (-7, -16, 3.0), (2, -5, 0.7), 28)
c5.keyframe_insert('location', frame=505)
c5.location = (-6.4, -15.2, 2.9); c5.keyframe_insert('location', frame=648)
c6, t6 = camera('cam6', (2.8, -12.8, 1.6), (13, 3, 0.9), 38)

for nm, fr, cam in (('S1', 1, c1), ('S2', 97, c2), ('S3', 193, c3),
                    ('S4', 313, c4), ('S5', 505, c5), ('S6', 649, c6)):
    mk = sc.timeline_markers.new(nm, frame=fr)
    mk.camera = cam
sc.camera = c1

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "borrowed_music_animatic.blend"))
sc.render.image_settings.file_format = 'JPEG'
if MODE == 'still':
    for f in (48, 150, 260, 460, 600, 690):
        sc.frame_set(f)
        sc.render.filepath = f"{OUT}/chk_f{f:03d}.jpg"
        bpy.ops.render.render(write_still=True)
else:
    if MODE.startswith("range"):
        _, a, bfr = MODE.split(":")
        sc.frame_start, sc.frame_end = int(a), int(bfr)
    os.makedirs(f"{OUT}/anim", exist_ok=True)
    sc.render.filepath = f"{OUT}/anim/f"
    bpy.ops.render.render(animation=True)
print("ANIMATIC DONE", MODE)
