#!/usr/bin/env python3
"""Borrowed Music — STAGE 4 production pass. Animatic timing + lookdev
materials/lighting; S04 redone on camera-facing flank with animated bend.
Run: blender -b --python build_production.py -- <outdir> ext1|int|ext2|still
  ext1 = EEVEE  f1-96    (S01)
  int  = CYCLES f97-504  (S02-04, 40 samples denoised)
  ext2 = EEVEE  f505-708 (S05-06)"""
import bpy, sys, os, math, random

argv = sys.argv[sys.argv.index("--") + 1:]
OUT, MODE = argv[0], argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = 640, 360
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, 708
sc.view_settings.view_transform = 'Filmic'
sc.view_settings.look = 'Medium High Contrast'

def node(nt, kind, **kw):
    n = nt.nodes.new(kind)
    for k, v in kw.items():
        if k == 'inputs':
            for ik, iv in v.items(): n.inputs[ik].default_value = iv
        else: setattr(n, k, v)
    return n

def base_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree, next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')

def simple_mat(name, color, rough=0.7, emit=0.0, emit_col=None):
    m, nt, b = base_mat(name)
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    if emit > 0:
        b.inputs['Emission Color'].default_value = (*(emit_col or color), 1)
        b.inputs['Emission Strength'].default_value = emit
    return m

def box(name, size, loc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=2, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    o.scale = (size[0]/2, size[1]/2, size[2]/2)
    o.data.materials.append(m); return o

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

# ========== lookdev prototype materials ==========
def mat_membrane(name, seed=0):
    m, nt, b = base_mat(name)
    b.inputs['Base Color'].default_value = (0.42, 0.45, 0.50, 1)
    b.inputs['Transmission Weight'].default_value = 0.45
    b.inputs['IOR'].default_value = 1.32
    n1 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 6.5 + seed})
    mr = node(nt, 'ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = 0.06; mr.inputs['To Max'].default_value = 0.42
    nt.links.new(n1.outputs['Fac'], mr.inputs['Value']); nt.links.new(mr.outputs[0], b.inputs['Roughness'])
    n2 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 4.0 + seed * 0.7})
    gt = node(nt, 'ShaderNodeMath', operation='GREATER_THAN', inputs={1: 0.74})
    ml = node(nt, 'ShaderNodeMath', operation='MULTIPLY', inputs={1: 0.35})
    nt.links.new(n2.outputs['Fac'], gt.inputs[0]); nt.links.new(gt.outputs[0], ml.inputs[0])
    nt.links.new(ml.outputs[0], b.inputs['Emission Strength'])
    b.inputs['Emission Color'].default_value = (0.55, 0.60, 0.75, 1)
    tc = node(nt, 'ShaderNodeTexCoord'); sep = node(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    n3 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 9.0})
    ad = node(nt, 'ShaderNodeMath', operation='MULTIPLY_ADD', inputs={1: 0.25, 2: 0.0})
    nt.links.new(n3.outputs['Fac'], ad.inputs[0])
    edge = node(nt, 'ShaderNodeMath', operation='ADD')
    nt.links.new(sep.outputs['Z'], edge.inputs[0]); nt.links.new(ad.outputs[0], edge.inputs[1])
    gt2 = node(nt, 'ShaderNodeMath', operation='GREATER_THAN', inputs={1: 0.22})
    nt.links.new(edge.outputs[0], gt2.inputs[0]); nt.links.new(gt2.outputs[0], b.inputs['Alpha'])
    if hasattr(m, 'blend_method'): m.blend_method = 'BLEND'
    return m

def mat_fiber(name, seed=0):
    m, nt, b = base_mat(name)
    b.inputs['Base Color'].default_value = (0.10, 0.10, 0.12, 1)
    b.inputs['Roughness'].default_value = 0.40
    tc = node(nt, 'ShaderNodeTexCoord'); mp = node(nt, 'ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (14 + seed, 1, 1)
    nt.links.new(tc.outputs['Generated'], mp.inputs[0])
    wav = node(nt, 'ShaderNodeTexWave', inputs={'Distortion': 2.6, 'Scale': 1.0})
    nt.links.new(mp.outputs[0], wav.inputs['Vector'])
    ramp = node(nt, 'ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.42; ramp.color_ramp.elements[1].position = 0.52
    nt.links.new(wav.outputs['Fac'], ramp.inputs[0]); nt.links.new(ramp.outputs[0], b.inputs['Alpha'])
    n2 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 22.0 + seed})
    gt = node(nt, 'ShaderNodeMath', operation='GREATER_THAN', inputs={1: 0.90})
    ml = node(nt, 'ShaderNodeMath', operation='MULTIPLY', inputs={1: 2.2})
    nt.links.new(n2.outputs['Fac'], gt.inputs[0]); nt.links.new(gt.outputs[0], ml.inputs[0])
    nt.links.new(ml.outputs[0], b.inputs['Emission Strength'])
    b.inputs['Emission Color'].default_value = (0.7, 0.72, 0.8, 1)
    if hasattr(m, 'blend_method'): m.blend_method = 'BLEND'
    return m

def mat_film(name, seed=0):
    m, nt, b = base_mat(name)
    b.inputs['Base Color'].default_value = (0.30, 0.27, 0.23, 1)
    b.inputs['IOR'].default_value = 1.45
    n1 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 3.0 + seed * 0.5})
    mr = node(nt, 'ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = 0.15; mr.inputs['To Max'].default_value = 0.62
    nt.links.new(n1.outputs['Fac'], mr.inputs['Value'])
    nt.links.new(mr.outputs[0], b.inputs['Transmission Weight'])
    tc = node(nt, 'ShaderNodeTexCoord'); mp = node(nt, 'ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1.2, 7.5, 1)
    nt.links.new(tc.outputs['Generated'], mp.inputs[0])
    n2 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 4.5, 'Detail': 6.0})
    nt.links.new(mp.outputs[0], n2.inputs['Vector'])
    bmp = node(nt, 'ShaderNodeBump', inputs={'Strength': 0.45})
    nt.links.new(n2.outputs['Fac'], bmp.inputs['Height']); nt.links.new(bmp.outputs[0], b.inputs['Normal'])
    mp2 = node(nt, 'ShaderNodeMapping'); mp2.inputs['Scale'].default_value = (60, 1.5, 1)
    nt.links.new(tc.outputs['Generated'], mp2.inputs[0])
    n3 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 2.0})
    nt.links.new(mp2.outputs[0], n3.inputs['Vector'])
    mr2 = node(nt, 'ShaderNodeMapRange')
    mr2.inputs['To Min'].default_value = 0.12; mr2.inputs['To Max'].default_value = 0.55
    nt.links.new(n3.outputs['Fac'], mr2.inputs['Value']); nt.links.new(mr2.outputs[0], b.inputs['Roughness'])
    return m

def mat_veil(name):
    m, nt, b = base_mat(name)
    b.inputs['Base Color'].default_value = (0.022, 0.022, 0.028, 1)
    b.inputs['Sheen Weight'].default_value = 0.9
    b.inputs['Transmission Weight'].default_value = 0.10
    b.inputs['Alpha'].default_value = 0.93
    vor = node(nt, 'ShaderNodeTexVoronoi', inputs={'Scale': 7.0})
    lt = node(nt, 'ShaderNodeMath', operation='LESS_THAN', inputs={1: 0.03})
    ml = node(nt, 'ShaderNodeMath', operation='MULTIPLY', inputs={1: 3.0})
    nt.links.new(vor.outputs['Distance'], lt.inputs[0]); nt.links.new(lt.outputs[0], ml.inputs[0])
    fr = node(nt, 'ShaderNodeFresnel', inputs={'IOR': 1.06})
    ml2 = node(nt, 'ShaderNodeMath', operation='MULTIPLY', inputs={1: 0.20})
    nt.links.new(fr.outputs[0], ml2.inputs[0])
    ad = node(nt, 'ShaderNodeMath', operation='ADD')
    nt.links.new(ml.outputs[0], ad.inputs[0]); nt.links.new(ml2.outputs[0], ad.inputs[1])
    nt.links.new(ad.outputs[0], b.inputs['Emission Strength'])
    b.inputs['Emission Color'].default_value = (0.60, 0.65, 0.85, 1)
    n1 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 12.0, 'Detail': 5.0})
    mr = node(nt, 'ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = 0.35; mr.inputs['To Max'].default_value = 0.75
    nt.links.new(n1.outputs['Fac'], mr.inputs['Value']); nt.links.new(mr.outputs[0], b.inputs['Roughness'])
    if hasattr(m, 'blend_method'): m.blend_method = 'BLEND'
    return m

# ========== EXT set (from animatic, unchanged) ==========
m_ground = simple_mat('ground', (0.030, 0.028, 0.026), 0.95)
m_hab = simple_mat('habitat', (0.10, 0.10, 0.11), 0.6)
m_winh = simple_mat('hab_window', (0.9, 0.75, 0.5), 0.4, emit=3.0, emit_col=(1.0, 0.8, 0.55))
m_rover = simple_mat('rover', (0.06, 0.06, 0.065), 0.7)
m_suit = simple_mat('suit', (0.26, 0.26, 0.29), 0.5)
m_shadowobj = simple_mat('anomaly', (0.012, 0.012, 0.014), 0.9)
box('ground', (300, 300, 0.05), (0, 0, -0.025), m_ground)
hab = sph('habitat_dome', 3.2, (0, 0, 0.4), m_hab); hab.scale = (1, 1, 0.62)
box('airlock', (1.4, 0.9, 1.9), (0, -3.0, 0.95), m_hab)
box('hab_win', (1.8, 0.05, 0.28), (0.4, -2.95, 1.35), m_winh)
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
    m_patch = simple_mat(prefix + '_patch', (0.03, 0.03, 0.04), 0.5)
    _pb = next(n for n in m_patch.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    _pb.inputs['Emission Color'].default_value = (0.45, 0.52, 0.70, 1)
    g['patch'] = box(prefix + '_patchobj', (0.03, 0.22, 0.34), (loc[0] - 0.25, loc[1], 1.05), m_patch)
    for k in ('head', 'pack', 'patch'):
        g[k].parent = g['body']
        g[k].matrix_parent_inverse = g['body'].matrix_world.inverted()
    return g

ext_ast = astronaut('ext', (0.8, -3.6, 0))
b = ext_ast['body']
b.location = (0.8, -3.6, -6.0); b.keyframe_insert('location', frame=504)
b.location = (0.8, -3.6, 0.78); b.keyframe_insert('location', frame=505)
b.location = (6.5, -9.5, 0.78); b.keyframe_insert('location', frame=640)
b.keyframe_insert('location', frame=708)
pb = ext_ast['patch'].data.materials[0].node_tree.nodes
pbb = next(n for n in pb if n.type == 'BSDF_PRINCIPLED').inputs['Emission Strength']
for f, v in [(504, 0.0), (552, 0.0), (566, 0.30), (680, 0.30), (683, 0.08), (690, 0.27)]:
    pbb.default_value = v; pbb.keyframe_insert('default_value', frame=f)
an = box('anomaly', (3.2, 0.25, 1.5), (26, 14, 0.9), m_shadowobj)
an.keyframe_insert('location', frame=660)
an.location = (22, 17, 0.9); an.keyframe_insert('location', frame=706)
bpy.ops.object.light_add(type='SUN')
sun = bpy.context.object
sun.rotation_euler = (math.radians(70), 0, math.radians(-30))
sun.data.energy = 0.45; sun.data.color = (0.72, 0.80, 1.0); sun.data.angle = 0.05
sun.data.keyframe_insert('energy', frame=678)
sun.data.energy = 0.34; sun.data.keyframe_insert('energy', frame=682)
sun.data.energy = 0.45; sun.data.keyframe_insert('energy', frame=688)
rv.keyframe_insert('rotation_euler', frame=608)
rv.rotation_euler = (0, 0.010, 0); rv.keyframe_insert('rotation_euler', frame=610)
rv.rotation_euler = (0, -0.006, 0); rv.keyframe_insert('rotation_euler', frame=612)
rv.rotation_euler = (0, 0, 0); rv.keyframe_insert('rotation_euler', frame=615)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
nt = w.node_tree
bgn = next(n for n in nt.nodes if n.type == 'BACKGROUND')
vor = node(nt, 'ShaderNodeTexVoronoi', inputs={'Scale': 140.0})
lt = node(nt, 'ShaderNodeMath', operation='LESS_THAN', inputs={1: 0.028})
ml = node(nt, 'ShaderNodeMath', operation='MULTIPLY', inputs={1: 6.0})
nt.links.new(vor.outputs['Distance'], lt.inputs[0]); nt.links.new(lt.outputs[0], ml.inputs[0])
nt.links.new(ml.outputs[0], bgn.inputs['Strength'])
bgn.inputs[0].default_value = (0.85, 0.88, 1.0, 1)

# ========== INT set (x+100) with lookdev upgrades ==========
X = 100.0
m_room = simple_mat('room', (0.045, 0.048, 0.055), 0.85)
m_ward = simple_mat('ward', (0.055, 0.05, 0.048), 0.65)
m_rail = simple_mat('rail', (0.22, 0.22, 0.23), 0.3)
box('floor_i', (8, 8, 0.05), (X, 0, -0.025), m_room)
box('ceil_i', (8, 8, 0.05), (X, 0, 2.62), m_room)
box('wall_b_i', (8, 0.05, 2.6), (X, 2.0, 1.3), m_room)
box('wall_l_i', (0.05, 8, 2.6), (X - 3.0, 0, 1.3), m_room)
box('wall_r_i', (0.05, 8, 2.6), (X + 3.0, 0, 1.3), m_room)
box('ward_back', (2.4, 0.04, 2.0), (X, 1.9, 1.15), m_ward)
box('ward_l', (0.04, 0.6, 2.0), (X - 1.2, 1.6, 1.15), m_ward)
box('ward_r', (0.04, 0.6, 2.0), (X + 1.2, 1.6, 1.15), m_ward)
box('ward_top', (2.4, 0.6, 0.04), (X, 1.6, 2.15), m_ward)
box('ward_bot', (2.4, 0.6, 0.04), (X, 1.6, 0.15), m_ward)
cyl('rail', 0.015, 2.3, (X, 1.55, 1.85), m_rail, rot=(0, math.pi/2, 0))
for side, hx in (('l', X - 1.2), ('r', X + 1.2)):
    bpy.ops.object.empty_add(location=(hx, 1.3, 1.15))
    hinge = bpy.context.object; hinge.name = f'hinge_{side}'
    d = box(f'door_{side}', (1.2, 0.03, 2.0), (hx + (0.6 if side == 'l' else -0.6), 1.3, 1.15), m_ward)
    d.parent = hinge; d.matrix_parent_inverse = hinge.matrix_world.inverted()
    ang = math.radians(115 if side == 'l' else -115)
    hinge.keyframe_insert('rotation_euler', frame=117)
    hinge.rotation_euler = (0, 0, ang); hinge.keyframe_insert('rotation_euler', frame=157)

def film_plane(name, w_, h_, loc, m, subdiv=12, wave=0.012):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    o = bpy.context.object; o.name = name
    o.scale = (w_, 1, h_)
    o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(m)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=subdiv)
    bpy.ops.object.mode_set(mode='OBJECT')
    tx = bpy.data.textures.new(name + '_tx', 'CLOUDS'); tx.noise_scale = 0.28
    dm = o.modifiers.new('disp', 'DISPLACE'); dm.texture = tx; dm.strength = wave; dm.direction = 'Y'
    return o

random.seed(4)
kinds = ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'V', 'B', 'C']
films = []
for i, kind in enumerate(kinds):
    fx = X - 0.95 + i * 0.21
    cyl(f'hook_{i}', 0.006, 0.10, (fx, 1.55, 1.80), m_rail, v=8)
    w_ = 0.075 + random.uniform(-0.012, 0.02)
    h_ = 0.62 + random.uniform(-0.08, 0.12)
    if kind == 'A': mm = mat_membrane(f'mA_{i}', seed=i)
    elif kind == 'B': mm = mat_fiber(f'mB_{i}', seed=i)
    elif kind == 'C': mm = mat_film(f'mC_{i}', seed=i)
    else: mm = mat_veil('m_veil')
    o = film_plane(f'film_{i}', w_, h_ if kind != 'V' else 0.68,
                   (fx, 1.53, 1.75 - (h_ if kind != 'V' else 0.68)), mm,
                   wave=0.02 if kind == 'V' else 0.012)
    films.append(o)
    if kind == 'V':
        continue
    for kf, a in ((97, 0.015), (250, -0.02), (400, 0.012), (560, -0.01), (708, 0.015)):
        o.rotation_euler = (math.radians(90) + a * ((i % 3) - 1), a * 0.7, 0)
        o.keyframe_insert('rotation_euler', frame=kf + i * 7)
veil = films[7]

# touch pulses = small point lights (art-directable, avoids linked-emission surgery)
for fi, fr in ((1, 204), (3, 230), (5, 254), (8, 278), (7, 298)):
    o = films[fi]
    bpy.ops.object.light_add(type='POINT', location=(o.location.x, 1.30, 1.45))
    Lp = bpy.context.object; Lp.data.color = (0.75, 0.8, 1.0); Lp.data.shadow_soft_size = 0.12
    for f, v in ((fr - 4, 0.0), (fr, 2.6), (fr + 14, 0.0)):
        Lp.data.energy = v; Lp.data.keyframe_insert('energy', frame=f)

# interior astronaut + arm
AX = X - 0.85
int_ast = astronaut('int', (AX, -0.7, 0))
int_ast['patch'].scale = (0.001, 0.001, 0.001)   # int patch off: the real veil IS the attached music
arm = cyl('int_arm', 0.05, 0.7, (AX + 0.1, -0.30, 1.30), m_suit, rot=(math.radians(75), 0, 0))
arm.keyframe_insert('location', frame=193)
for fr, fx in ((204, X - 0.74), (230, X - 0.32), (254, X + 0.10), (278, X + 0.73), (298, X + 0.52)):
    arm.location = (fx, 0.35, 1.45); arm.keyframe_insert('location', frame=fr)
arm.location = (AX + 0.1, -0.30, 1.30); arm.keyframe_insert('location', frame=340)
arm.keyframe_insert('location', frame=425)
arm.location = (X + 0.50, 0.30, 1.48); arm.keyframe_insert('location', frame=445)
arm.location = (AX + 0.1, -0.30, 1.30); arm.keyframe_insert('location', frame=488)

# S04 veil flight: hanger -> camera-facing flank (lookdev-verified layout), animated bend
sdv = veil.modifiers.new('bend', 'SIMPLE_DEFORM')
sdv.deform_method = 'BEND'; sdv.deform_axis = 'Z'; sdv.angle = 0.0
sdv.keyframe_insert('angle', frame=440)
veil.keyframe_insert('location', frame=440)
veil.keyframe_insert('rotation_euler', frame=440)
veil.keyframe_insert('scale', frame=440)
veil.location = (AX - 0.52, -0.55, 1.22)
veil.rotation_euler = (math.radians(72), math.radians(-18), math.radians(-35))
sdv.angle = math.radians(40)
veil.keyframe_insert('location', frame=468); veil.keyframe_insert('rotation_euler', frame=468)
sdv.keyframe_insert('angle', frame=468)
veil.location = (AX - 0.265, -0.68, 1.06)
veil.rotation_euler = (math.radians(88), 0, math.radians(-90))
sdv.angle = math.radians(160)
veil.keyframe_insert('location', frame=490); veil.keyframe_insert('rotation_euler', frame=490)
sdv.keyframe_insert('angle', frame=490)
# interior lighting (lookdev design)
bpy.ops.object.light_add(type='AREA', location=(X - 2.0, -2.2, 2.35))
L1 = bpy.context.object; L1.data.energy = 14; L1.data.size = 2.0
L1.data.color = (0.70, 0.78, 0.95); L1.rotation_euler = (math.radians(35), 0, math.radians(-20))
bpy.ops.object.light_add(type='AREA', location=(X, 1.82, 1.25))
L2 = bpy.context.object; L2.data.size = 2.2; L2.data.color = (0.82, 0.85, 1.0)
L2.rotation_euler = (math.radians(-100), 0, 0)
for f, v in ((117, 0.0), (160, 10.0)):
    L2.data.energy = v; L2.data.keyframe_insert('energy', frame=f)
bpy.ops.object.light_add(type='POINT', location=(X + 2.3, -0.4, 1.8))
L3 = bpy.context.object; L3.data.energy = 4; L3.data.color = (1.0, 0.72, 0.45)
# S04 side fill (lookdev) only during S04
bpy.ops.object.light_add(type='AREA', location=(X - 1.5, -1.6, 1.8))
L4 = bpy.context.object; L4.data.size = 1.4; L4.data.color = (0.72, 0.78, 0.95)
L4.rotation_euler = (math.radians(-35), math.radians(-25), 0)
for f, v in ((312, 0.0), (318, 3.5), (500, 3.5), (504, 0.0)):
    L4.data.energy = v; L4.data.keyframe_insert('energy', frame=f)

# ========== cameras & markers ==========
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
c2, t2 = camera('cam2', (X + 0.55, -3.05, 1.55), (X + 0.05, 1.4, 1.32), 32)
c3, t3 = camera('cam3', (X - 1.9, -1.05, 1.62), (X + 0.15, 1.55, 1.35), 30)
c3.keyframe_insert('location', frame=193); t3.keyframe_insert('location', frame=193)
c3.location = (X - 0.55, -1.05, 1.55); t3.location = (X + 0.7, 1.55, 1.30)
c3.keyframe_insert('location', frame=312); t3.keyframe_insert('location', frame=312)
# S04: side camera on the flank (lookdev framing, wider to include hanger at start)
c4, t4 = camera('cam4', (X - 2.15, -1.15, 1.38), (X + 0.15, 0.45, 1.20), 40)
c4.keyframe_insert('location', frame=313); t4.keyframe_insert('location', frame=313)
c4.keyframe_insert('location', frame=430); t4.keyframe_insert('location', frame=430)
c4.location = (AX - 1.85, -1.55, 1.34); t4.location = (AX + 0.1, -0.55, 1.10)
c4.keyframe_insert('location', frame=470); t4.keyframe_insert('location', frame=470)
c5, t5 = camera('cam5', (-7, -16, 3.0), (2, -5, 0.7), 28)
c5.keyframe_insert('location', frame=505)
c5.location = (-6.4, -15.2, 2.9); c5.keyframe_insert('location', frame=648)
c6, t6 = camera('cam6', (2.8, -12.8, 1.6), (13, 3, 0.9), 38)
for nm, fr, cam in (('S1', 1, c1), ('S2', 97, c2), ('S3', 193, c3),
                    ('S4', 313, c4), ('S5', 505, c5), ('S6', 649, c6)):
    mk = sc.timeline_markers.new(nm, frame=fr)
    mk.camera = cam
sc.camera = c1

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "borrowed_music_production.blend"))
sc.render.image_settings.file_format = 'JPEG'
os.makedirs(f"{OUT}/prod", exist_ok=True)
sc.render.filepath = f"{OUT}/prod/f"
if MODE == 'ext1':
    sc.render.engine = 'BLENDER_EEVEE'
    sc.frame_start, sc.frame_end = 1, 96
    bpy.ops.render.render(animation=True)
elif MODE == 'int':
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 40; sc.cycles.use_denoising = True
    sc.frame_start, sc.frame_end = 97, 504
    bpy.ops.render.render(animation=True)
elif MODE == 'ext2':
    sc.render.engine = 'BLENDER_EEVEE'
    sc.frame_start, sc.frame_end = 505, 708
    bpy.ops.render.render(animation=True)
elif MODE == 'still':
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 40; sc.cycles.use_denoising = True
    for f in (460, 496):
        sc.frame_set(f)
        sc.render.filepath = f"{OUT}/chk_f{f:03d}.jpg"
        bpy.ops.render.render(write_still=True)
    sc.render.engine = 'BLENDER_EEVEE'
    for f in (48, 600, 690):
        sc.frame_set(f)
        sc.render.filepath = f"{OUT}/chk_f{f:03d}.jpg"
        bpy.ops.render.render(write_still=True)
print("PRODUCTION DONE", MODE)
