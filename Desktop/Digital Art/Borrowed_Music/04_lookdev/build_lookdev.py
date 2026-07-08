#!/usr/bin/env python3
"""Borrowed Music STAGE 3 — hero look development (interior set only, Cycles
stills, low samples). 3 music prototypes (membrane/fiber/film) + hero dark
veil; S02 wardrobe-open hero; S04 attach in 3 states via SimpleDeform bend.
Run: blender -b --python build_lookdev.py -- <outdir> s02|protos|s04a|s04b|s04c"""
import bpy, sys, os, math, random

argv = sys.argv[sys.argv.index("--") + 1:]
OUT, MODE = argv[0], argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 96
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 960, 540
sc.view_settings.view_transform = 'Filmic'
sc.view_settings.look = 'Medium High Contrast'

X = 0.0  # lookdev set at origin

def node(nt, kind, **kw):
    n = nt.nodes.new(kind)
    for k, v in kw.items():
        if k == 'inputs':
            for ik, iv in v.items(): n.inputs[ik].default_value = iv
        else: setattr(n, k, v)
    return n

def base_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    return m, nt, b

def simple_mat(name, color, rough=0.7):
    m, nt, b = base_mat(name)
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    return m

def box(name, size, loc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=2, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    o.scale = (size[0]/2, size[1]/2, size[2]/2)
    o.data.materials.append(m); return o

def cyl(name, r, h, loc, m, rot=(0, 0, 0), v=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth = True
    return o

# ---------- room / wardrobe (reuse greybox layout, darker) ----------
m_room = simple_mat('room', (0.045, 0.048, 0.055), 0.85)
m_ward = simple_mat('ward', (0.055, 0.05, 0.048), 0.65)
m_rail = simple_mat('rail', (0.22, 0.22, 0.23), 0.3)
box('floor', (8, 8, 0.05), (X, 0, -0.025), m_room)
box('ceil', (8, 8, 0.05), (X, 0, 2.62), m_room)
box('wall_b', (8, 0.05, 2.6), (X, 2.0, 1.3), m_room)
box('wall_l', (0.05, 8, 2.6), (X - 3.0, 0, 1.3), m_room)
box('wall_r', (0.05, 8, 2.6), (X + 3.0, 0, 1.3), m_room)
box('ward_back', (2.4, 0.04, 2.0), (X, 1.9, 1.15), m_ward)
box('ward_l', (0.04, 0.6, 2.0), (X - 1.2, 1.6, 1.15), m_ward)
box('ward_r', (0.04, 0.6, 2.0), (X + 1.2, 1.6, 1.15), m_ward)
box('ward_top', (2.4, 0.6, 0.04), (X, 1.6, 2.15), m_ward)
box('ward_bot', (2.4, 0.6, 0.04), (X, 1.6, 0.15), m_ward)
cyl('rail', 0.015, 2.3, (X, 1.55, 1.85), m_rail, rot=(0, math.pi/2, 0))
# open doors (parked at 115°)
for side, hx, ang in (('l', X - 1.2, 115), ('r', X + 1.2, -115)):
    d = box(f'door_{side}', (1.2, 0.03, 2.0), (0.6, 0, 0), m_ward)
    d.location = (hx + 0.6 * math.cos(math.radians(ang)) * (1 if side == 'l' else -1),
                  1.3 + 0.6 * math.sin(math.radians(abs(ang))) * -1, 1.15)
    d.rotation_euler = (0, 0, math.radians(ang))

# ---------- prototype materials ----------
def mat_membrane(name, seed=0):
    m, nt, b = base_mat(name)
    m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else None
    b.inputs['Base Color'].default_value = (0.42, 0.45, 0.50, 1)
    b.inputs['Transmission Weight'].default_value = 0.45
    b.inputs['IOR'].default_value = 1.32
    n1 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 6.5 + seed})
    mr = node(nt, 'ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = 0.06; mr.inputs['To Max'].default_value = 0.42
    nt.links.new(n1.outputs['Fac'], mr.inputs['Value'])
    nt.links.new(mr.outputs[0], b.inputs['Roughness'])
    # faint interior dark-light patches
    n2 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 4.0 + seed * 0.7})
    gt = node(nt, 'ShaderNodeMath', operation='GREATER_THAN', inputs={1: 0.74})
    ml = node(nt, 'ShaderNodeMath', operation='MULTIPLY', inputs={1: 0.35})
    nt.links.new(n2.outputs['Fac'], gt.inputs[0])
    nt.links.new(gt.outputs[0], ml.inputs[0])
    nt.links.new(ml.outputs[0], b.inputs['Emission Strength'])
    b.inputs['Emission Color'].default_value = (0.55, 0.60, 0.75, 1)
    # ragged lower edge via alpha
    tc = node(nt, 'ShaderNodeTexCoord')
    sep = node(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    n3 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 9.0})
    add = node(nt, 'ShaderNodeMath', operation='MULTIPLY_ADD', inputs={1: 0.25, 2: 0.0})
    nt.links.new(n3.outputs['Fac'], add.inputs[0])
    edge = node(nt, 'ShaderNodeMath', operation='ADD')
    nt.links.new(sep.outputs['Z'], edge.inputs[0])
    nt.links.new(add.outputs[0], edge.inputs[1])
    gt2 = node(nt, 'ShaderNodeMath', operation='GREATER_THAN', inputs={1: 0.22})
    nt.links.new(edge.outputs[0], gt2.inputs[0])
    nt.links.new(gt2.outputs[0], b.inputs['Alpha'])
    return m

def mat_fiber(name, seed=0):
    m, nt, b = base_mat(name)
    b.inputs['Base Color'].default_value = (0.10, 0.10, 0.12, 1)
    b.inputs['Roughness'].default_value = 0.40
    tc = node(nt, 'ShaderNodeTexCoord')
    mp = node(nt, 'ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (14 + seed, 1, 1)
    nt.links.new(tc.outputs['Generated'], mp.inputs[0])
    wav = node(nt, 'ShaderNodeTexWave', inputs={'Distortion': 2.6, 'Scale': 1.0})
    nt.links.new(mp.outputs[0], wav.inputs['Vector'])
    ramp = node(nt, 'ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.42
    ramp.color_ramp.elements[1].position = 0.52
    nt.links.new(wav.outputs['Fac'], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], b.inputs['Alpha'])   # strands
    # sparse dim points along strands
    n2 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 22.0 + seed})
    gt = node(nt, 'ShaderNodeMath', operation='GREATER_THAN', inputs={1: 0.90})
    ml = node(nt, 'ShaderNodeMath', operation='MULTIPLY', inputs={1: 2.2})
    nt.links.new(n2.outputs['Fac'], gt.inputs[0]); nt.links.new(gt.outputs[0], ml.inputs[0])
    nt.links.new(ml.outputs[0], b.inputs['Emission Strength'])
    b.inputs['Emission Color'].default_value = (0.7, 0.72, 0.8, 1)
    return m

def mat_film(name, seed=0):
    m, nt, b = base_mat(name)
    b.inputs['Base Color'].default_value = (0.30, 0.27, 0.23, 1)
    b.inputs['IOR'].default_value = 1.45
    # uneven transmission (storage wear)
    n1 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 3.0 + seed * 0.5})
    mr = node(nt, 'ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = 0.15; mr.inputs['To Max'].default_value = 0.62
    nt.links.new(n1.outputs['Fac'], mr.inputs['Value'])
    nt.links.new(mr.outputs[0], b.inputs['Transmission Weight'])
    # creases: stretched noise bump
    tc = node(nt, 'ShaderNodeTexCoord'); mp = node(nt, 'ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1.2, 7.5, 1)
    nt.links.new(tc.outputs['Generated'], mp.inputs[0])
    n2 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 4.5, 'Detail': 6.0})
    nt.links.new(mp.outputs[0], n2.inputs['Vector'])
    bmp = node(nt, 'ShaderNodeBump', inputs={'Strength': 0.45})
    nt.links.new(n2.outputs['Fac'], bmp.inputs['Height'])
    nt.links.new(bmp.outputs[0], b.inputs['Normal'])
    # scratches -> roughness streaks
    mp2 = node(nt, 'ShaderNodeMapping'); mp2.inputs['Scale'].default_value = (60, 1.5, 1)
    nt.links.new(tc.outputs['Generated'], mp2.inputs[0])
    n3 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 2.0})
    nt.links.new(mp2.outputs[0], n3.inputs['Vector'])
    mr2 = node(nt, 'ShaderNodeMapRange')
    mr2.inputs['To Min'].default_value = 0.12; mr2.inputs['To Max'].default_value = 0.55
    nt.links.new(n3.outputs['Fac'], mr2.inputs['Value'])
    nt.links.new(mr2.outputs[0], b.inputs['Roughness'])
    return m

def mat_veil(name):
    m, nt, b = base_mat(name)
    b.inputs['Base Color'].default_value = (0.022, 0.022, 0.028, 1)
    b.inputs['Roughness'].default_value = 0.55
    b.inputs['Sheen Weight'].default_value = 0.9
    b.inputs['Transmission Weight'].default_value = 0.10
    b.inputs['Alpha'].default_value = 0.93
    # rare star points
    vor = node(nt, 'ShaderNodeTexVoronoi', inputs={'Scale': 7.0})
    lt = node(nt, 'ShaderNodeMath', operation='LESS_THAN', inputs={1: 0.03})
    ml = node(nt, 'ShaderNodeMath', operation='MULTIPLY', inputs={1: 3.0})
    nt.links.new(vor.outputs['Distance'], lt.inputs[0]); nt.links.new(lt.outputs[0], ml.inputs[0])
    # weak grazing rim
    fr = node(nt, 'ShaderNodeFresnel', inputs={'IOR': 1.06})
    ml2 = node(nt, 'ShaderNodeMath', operation='MULTIPLY', inputs={1: 0.20})
    nt.links.new(fr.outputs[0], ml2.inputs[0])
    ad = node(nt, 'ShaderNodeMath', operation='ADD')
    nt.links.new(ml.outputs[0], ad.inputs[0]); nt.links.new(ml2.outputs[0], ad.inputs[1])
    nt.links.new(ad.outputs[0], b.inputs['Emission Strength'])
    b.inputs['Emission Color'].default_value = (0.60, 0.65, 0.85, 1)
    # roughness variation (sound residue)
    n1 = node(nt, 'ShaderNodeTexNoise', inputs={'Scale': 12.0, 'Detail': 5.0})
    mr = node(nt, 'ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = 0.35; mr.inputs['To Max'].default_value = 0.75
    nt.links.new(n1.outputs['Fac'], mr.inputs['Value'])
    nt.links.new(mr.outputs[0], b.inputs['Roughness'])
    return m

# ---------- music items on rail ----------
def film_plane(name, w, h, loc, m, subdiv=12, wave=0.012, seed=0):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    o = bpy.context.object; o.name = name
    o.scale = (w, 1, h)
    o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(m)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=subdiv)
    bpy.ops.object.mode_set(mode='OBJECT')
    tx = bpy.data.textures.new(name + '_tx', 'CLOUDS')
    tx.noise_scale = 0.28
    dm = o.modifiers.new('disp', 'DISPLACE')
    dm.texture = tx; dm.strength = wave; dm.direction = 'Y'
    return o

random.seed(4)
kinds = ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'V', 'B', 'C']
items = []
for i, kind in enumerate(kinds):
    fx = X - 0.95 + i * 0.21
    cyl(f'hook_{i}', 0.006, 0.10, (fx, 1.55, 1.80), m_rail, v=8)
    w = 0.075 + random.uniform(-0.012, 0.02)
    h = 0.62 + random.uniform(-0.08, 0.12)
    if kind == 'A': mm = mat_membrane(f'mA_{i}', seed=i)
    elif kind == 'B': mm = mat_fiber(f'mB_{i}', seed=i)
    elif kind == 'C': mm = mat_film(f'mC_{i}', seed=i)
    else: mm = mat_veil('m_veil')
    o = film_plane(f'film_{i}', w, h if kind != 'V' else 0.68,
                   (fx, 1.53, 1.75 - (h if kind != 'V' else 0.68) / 1.0), mm,
                   wave=0.02 if kind == 'V' else 0.012, seed=i)
    items.append(o)
veil = items[7]

# ---------- astronaut (darker suit) ----------
m_suit = simple_mat('suit', (0.26, 0.26, 0.29), 0.5)
ast_x = X - 0.85
body = cyl('ast_body', 0.24, 1.05, (ast_x, -0.7, 0.78), m_suit)
sphm = simple_mat('suit2', (0.17, 0.17, 0.19), 0.45)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=14, radius=0.17, location=(ast_x, -0.7, 1.52))
head = bpy.context.object; head.data.materials.append(sphm)
for p in head.data.polygons: p.use_smooth = True
box('ast_pack', (0.36, 0.18, 0.5), (ast_x, -0.94, 1.05), m_suit)

# ---------- lighting (dark, leak-lit) ----------
# faint cool room key
bpy.ops.object.light_add(type='AREA', location=(X - 2.0, -2.2, 2.35))
L1 = bpy.context.object; L1.data.energy = 14; L1.data.size = 2.0
L1.data.color = (0.70, 0.78, 0.95)
L1.rotation_euler = (math.radians(35), 0, math.radians(-20))
# backlight strip INSIDE wardrobe behind films (translucency reads)
bpy.ops.object.light_add(type='AREA', location=(X, 1.82, 1.25))
L2 = bpy.context.object; L2.data.energy = 10; L2.data.size = 2.2
L2.data.color = (0.82, 0.85, 1.0)
L2.rotation_euler = (math.radians(-100), 0, 0)
if hasattr(L2.data, 'size_y'): L2.data.size_y = 0.9
# tiny warm practical far right
bpy.ops.object.light_add(type='POINT', location=(X + 2.3, -0.4, 1.8))
L3 = bpy.context.object; L3.data.energy = 4; L3.data.color = (1.0, 0.72, 0.45)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bgn = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bgn.inputs[0].default_value = (0.02, 0.022, 0.03, 1); bgn.inputs[1].default_value = 0.35

def camera(loc, tgt, lens):
    bpy.ops.object.empty_add(location=tgt); t = bpy.context.object
    bpy.ops.object.camera_add(location=loc); c = bpy.context.object
    c.data.lens = lens
    tr = c.constraints.new('TRACK_TO'); tr.target = t
    tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    sc.camera = c
    return c

os.makedirs(OUT, exist_ok=True)
sc.render.image_settings.file_format = 'PNG'

def render(path):
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)

if MODE == 's02':
    camera((X + 0.55, -3.05, 1.55), (X + 0.05, 1.4, 1.32), 32)
    render(f"{OUT}/S02_base.png")
elif MODE == 'protos':
    # isolation stage: subject alone, centered, fixed camera + raking light
    body.location.z -= 30; head.location.z -= 30
    for o in items:
        o.location.z -= 30
    bpy.ops.object.light_add(type='AREA', location=(X - 0.7, -0.25, 1.5))
    Lg = bpy.context.object; Lg.data.energy = 14; Lg.data.size = 0.3
    Lg.data.color = (0.78, 0.82, 0.95)
    Lg.rotation_euler = (math.radians(-70), math.radians(-55), 0)
    bpy.ops.object.light_add(type='AREA', location=(X, 0.85, 1.35))
    Lb = bpy.context.object; Lb.data.energy = 7; Lb.data.size = 1.0
    Lb.data.color = (0.82, 0.85, 1.0)
    Lb.rotation_euler = (math.radians(-95), 0, 0)   # backlight toward camera
    cam = camera((X, -1.05, 1.32), (X, 0, 1.35), 50)
    for idx, nm in ((0, 'protoA_membrane'), (1, 'protoB_fiber'), (2, 'protoC_film'), (7, 'hero_veil')):
        o = items[idx]
        old = tuple(o.location)
        o.location = (X, 0, old[2] + 30 + 0.22)      # bring to stage, centered
        o.rotation_euler.z = math.radians(18)
        o.scale = (o.scale.x * 2.6, o.scale.y, o.scale.z * 1.6)
        Lb.data.energy = 2.5 if idx == 0 else (10 if idx == 1 else 7)
        Lg.data.energy = 26 if idx == 1 else 14
        render(f"{OUT}/{nm}.png")
        o.location = (old[0], old[1], old[2])
elif MODE in ('s04a', 's04b', 's04c'):
    # soft cool fill from camera side onto the action
    bpy.ops.object.light_add(type='AREA', location=(ast_x - 1.2, -1.9, 1.7))
    Ls = bpy.context.object; Ls.data.energy = 7; Ls.data.size = 1.4
    Ls.data.color = (0.72, 0.78, 0.95)
    Ls.rotation_euler = (math.radians(-35), math.radians(-25), 0)
    if MODE == 's04a':
        camera((X - 2.15, -1.15, 1.38), (X + 0.15, 0.45, 1.20), 40)
    else:
        camera((ast_x - 1.75, -1.15, 1.30), (ast_x + 0.1, -0.62, 1.10), 46)
        Ls.location = (ast_x - 1.5, -1.6, 1.8)
    if MODE == 's04a':      # leaving the hanger (peeled corner)
        veil.location = (veil.location.x, 1.42, veil.location.z + 0.03)
        veil.rotation_euler = (math.radians(75), math.radians(8), math.radians(6))
    elif MODE == 's04b':    # first contact: drifting toward camera-facing flank
        veil.location = (ast_x - 0.52, -0.55, 1.22)
        veil.rotation_euler = (math.radians(72), math.radians(-18), math.radians(-35))
        sd = veil.modifiers.new('bend', 'SIMPLE_DEFORM')
        sd.deform_method = 'BEND'; sd.angle = math.radians(40); sd.deform_axis = 'Z'
    else:                   # partial attach: wrapped onto the flank, lower edge floating
        veil.location = (ast_x - 0.265, -0.68, 1.06)
        veil.rotation_euler = (math.radians(88), 0, math.radians(-90))
        sd = veil.modifiers.new('bend', 'SIMPLE_DEFORM')
        sd.deform_method = 'BEND'; sd.angle = math.radians(160); sd.deform_axis = 'Z'
        veil.modifiers['disp'].strength = 0.035
    render(f"{OUT}/S04_{MODE[-1]}_base.png")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(OUT.rstrip('/')), "lookdev.blend"))
print("LOOKDEV DONE", MODE)
