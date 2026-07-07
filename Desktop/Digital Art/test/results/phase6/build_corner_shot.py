#!/usr/bin/env python3
"""Phase 6: Blender blocking of the New Orleans corner (from 2.imagetovideo.JPG
/ previs 'last patch of sun'). Spatial truth + camera + lighting states +
control passes. Run: blender -b --python build_corner_shot.py -- <outdir> still|anim|passes"""
import bpy, sys, os, math

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
MODE = argv[1] if len(argv) > 1 else "still"

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x, sc.render.resolution_y = 960, 640
sc.render.fps = 30
for attr in ('use_raytracing', 'use_ssr'):
    if hasattr(sc.eevee, attr): setattr(sc.eevee, attr, True)

def mat(name, color, rough=0.7, bump=0.0, emit=0.0, emit_col=(1, 1, 1)):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = rough
    if emit > 0:
        for k in ('Emission Color',):
            if k in bsdf.inputs: bsdf.inputs[k].default_value = (*emit_col, 1)
        if 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = emit
    if bump > 0:
        tex = nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = 38
        bmp = nt.nodes.new('ShaderNodeBump'); bmp.inputs['Strength'].default_value = bump
        nt.links.new(tex.outputs['Fac'], bmp.inputs['Height'])
        nt.links.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    return m

def box(name, size, loc, m, rot=(0, 0, 0), idx=0):
    bpy.ops.mesh.primitive_cube_add(size=2, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(m); o.pass_index = idx
    return o

def cyl(name, r, h, loc, m, rot=(0, 0, 0), idx=0, v=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    o.data.materials.append(m); o.pass_index = idx
    for p in o.data.polygons: p.use_smooth = True
    return o

m_red = mat('stucco_red', (0.45, 0.13, 0.09), 0.75, bump=0.25)
m_band = mat('band_white', (0.85, 0.83, 0.78), 0.6, bump=0.1)
m_ply = mat('plywood', (0.62, 0.45, 0.26), 0.65, bump=0.15)
m_door = mat('door_green', (0.16, 0.19, 0.16), 0.5)
m_win = mat('window_dark', (0.06, 0.07, 0.09), 0.15)
m_frame = mat('frame_white', (0.88, 0.87, 0.83), 0.5)
m_black = mat('metal_black', (0.03, 0.03, 0.03), 0.35)
m_street = mat('asphalt', (0.10, 0.10, 0.10), 0.9, bump=0.3)
m_walk = mat('sidewalk', (0.35, 0.33, 0.30), 0.85, bump=0.2)
m_sign = mat('sign_white', (0.85, 0.84, 0.80), 0.5)
m_lamp_glass = mat('lamp_glass', (0.9, 0.75, 0.5), 0.2, emit=0.0, emit_col=(1.0, 0.62, 0.28))

# ---- ground: street + sidewalk (corner) ----
box('street', (40, 40, 0.04), (0, 0, -0.02), m_street, idx=3)
box('sidewalk_a', (24, 3.4, 0.12), (0, -1.9, 0.06), m_walk, idx=3)
box('sidewalk_b', (3.4, 24, 0.12), (-1.9, 0, 0.06), m_walk, idx=3)

# ---- facades: A along +x (front), B along +y (side), corner at origin ----
H1, H2 = 4.6, 8.6   # floor heights
def facade(name, along, length, m=m_red):
    if along == 'x':
        box(name, (length, 0.5, H2), (length / 2, 0.25, H2 / 2), m, idx=1)
    else:
        box(name, (0.5, length, H2), (0.25, length / 2, H2 / 2), m, idx=1)
facade('facA', 'x', 16)
facade('facB', 'y', 16)
# white band between floors + top cornice
box('bandA', (16, 0.56, 0.35), (8, 0.25, H1), m_band, idx=1)
box('bandB', (0.56, 16, 0.35), (0.25, 8, H1), m_band, idx=1)
box('cornA', (16, 0.6, 0.3), (8, 0.25, H2), m_band, idx=1)
box('cornB', (0.6, 16, 0.3), (0.25, 8, H2), m_band, idx=1)

# ---- arched boarded doorways on facade A (plywood inset + green base + arch top) ----
def doorway(x, along='x'):
    if along == 'x':
        box(f'ply_{x:.0f}', (1.5, 0.12, 2.6), (x, -0.05, 1.7), m_ply, idx=1)
        box(f'dgrn_{x:.0f}', (1.5, 0.12, 0.7), (x, -0.05, 0.35), m_door, idx=1)
        cyl(f'arch_{x:.0f}', 0.72, 0.12, (x, -0.05, 2.65), m_ply, rot=(math.pi / 2, 0, 0), idx=1, v=32)
        box(f'lint_{x:.0f}', (1.9, 0.14, 0.14), (x, -0.06, 3.42), m_frame, idx=1)
    else:
        box(f'plyB_{x:.0f}', (0.12, 1.5, 2.6), (-0.05, x, 1.7), m_ply, idx=1)
        box(f'dgrnB_{x:.0f}', (0.12, 1.5, 0.7), (-0.05, x, 0.35), m_door, idx=1)
        cyl(f'archB_{x:.0f}', 0.72, 0.12, (-0.05, x, 2.65), m_ply, rot=(0, math.pi / 2, 0), idx=1, v=32)
        box(f'lintB_{x:.0f}', (0.14, 1.9, 0.14), (-0.06, x, 3.42), m_frame, idx=1)

for x in (2.2, 4.6, 7.0, 9.4, 11.8):
    doorway(x, 'x')
for y in (2.2, 4.6, 7.0):
    doorway(y, 'y')

# ---- upper windows ----
def window(x, along='x'):
    if along == 'x':
        box(f'win_{x:.0f}', (1.1, 0.1, 1.9), (x, -0.03, 6.6), m_win, idx=1)
        box(f'wfr_{x:.0f}', (1.3, 0.08, 0.14), (x, -0.05, 7.6), m_frame, idx=1)
        box(f'wsl_{x:.0f}', (1.3, 0.08, 0.14), (x, -0.05, 5.6), m_frame, idx=1)
    else:
        box(f'winB_{x:.0f}', (0.1, 1.1, 1.9), (-0.03, x, 6.6), m_win, idx=1)
        box(f'wfrB_{x:.0f}', (0.08, 1.3, 0.14), (-0.05, x, 7.6), m_frame, idx=1)
        box(f'wslB_{x:.0f}', (0.08, 1.3, 0.14), (-0.05, x, 5.6), m_frame, idx=1)

for x in (2.2, 4.6, 7.0, 9.4, 11.8):
    window(x, 'x')
for y in (2.2, 4.6, 7.0):
    window(y, 'y')

# ---- realty sign hanging near corner on facade A ----
box('sign', (1.1, 0.06, 1.5), (3.4, -0.45, 3.9), m_sign, idx=4)
cyl('sign_chain', 0.015, 0.9, (3.4, -0.35, 5.0), m_black, idx=4, v=8)

# ---- lamp pole at corner curb ----
cyl('pole', 0.09, 5.6, (-1.15, -1.15, 2.8), m_black, idx=2)
cyl('pole_base', 0.16, 1.2, (-1.15, -1.15, 0.6), m_black, idx=2)

# ---- two wall lanterns (emission driven per state) ----
lanterns = []
for i, (lx, ly, along) in enumerate([(1.15, -0.32, 'x'), (8.15, -0.32, 'x')]):
    b = box(f'lant_body_{i}', (0.22, 0.22, 0.5), (lx, ly, 3.4), m_black, idx=2)
    g = box(f'lant_glass_{i}', (0.16, 0.16, 0.3), (lx, ly, 3.38), m_lamp_glass, idx=2)
    lanterns.append(g)
# point lights inside lanterns (energy keyframed)
plights = []
for i, lx in enumerate((1.15, 8.15)):
    bpy.ops.object.light_add(type='POINT', location=(lx, -0.55, 3.35))
    L = bpy.context.object; L.data.energy = 0.0; L.data.color = (1.0, 0.55, 0.22)
    L.data.shadow_soft_size = 0.25
    plights.append(L)

# shadow-caster building across the street (throws diagonal shade onto corner)
box('caster', (6, 4, 8), (11.0, -13.5, 4.0), m_street, idx=0)

# ---- sun (hard low warm) + world ----
bpy.ops.object.light_add(type='SUN', location=(6, -10, 7))
sun = bpy.context.object
sun.rotation_euler = (math.radians(68), 0, math.radians(25))
sun.data.energy = 8.0; sun.data.color = (1.0, 0.74, 0.48); sun.data.angle = 0.02
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs[0].default_value = (0.55, 0.65, 0.85, 1); bg.inputs[1].default_value = 0.5

# ---- camera: slow push toward corner over 10s ----
bpy.ops.object.empty_add(location=(1.2, 1.2, 3.0)); tgt = bpy.context.object
bpy.ops.object.camera_add(location=(10.5, -10.5, 1.7))
cam = bpy.context.object; sc.camera = cam
cam.data.lens = 30
cam.data.dof.use_dof = True
cam.data.dof.focus_object = tgt
cam.data.dof.aperture_fstop = 4.0
tr = cam.constraints.new('TRACK_TO'); tr.target = tgt
tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'

N = 300
sc.frame_start, sc.frame_end = 1, N
for f, pos in [(1, (10.5, -10.5, 1.7)), (N, (6.8, -6.8, 1.6))]:
    cam.location = pos; cam.keyframe_insert('location', frame=f)

# ---- lighting states: GOLD (1-150) -> DUSK (150-200) -> NIGHT (200-300) ----
def key(obj_data, prop, frame, value):
    setattr(obj_data, prop, value)
    obj_data.keyframe_insert(prop, frame=frame)

key(sun.data, 'energy', 1, 8.0); key(sun.data, 'energy', 150, 8.0); key(sun.data, 'energy', 200, 0.0)
key(bg.inputs[1], 'default_value', 1, 0.5)
key(bg.inputs[1], 'default_value', 150, 0.5)
key(bg.inputs[1], 'default_value', 210, 0.075)
bg.inputs[0].default_value = (0.55, 0.65, 0.85, 1)
bg.inputs[0].keyframe_insert('default_value', frame=150)
bg.inputs[0].default_value = (0.12, 0.16, 0.32, 1)
bg.inputs[0].keyframe_insert('default_value', frame=210)
for i, L in enumerate(plights):
    on = 212 + i * 24
    key(L.data, 'energy', on, 0.0)
    key(L.data, 'energy', on + 6, 95.0)
# lantern glass emission via material keyframes
for i, g in enumerate(lanterns):
    bsdf = next(n for n in g.data.materials[0].node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    if 'Emission Strength' in bsdf.inputs:
        es = bsdf.inputs['Emission Strength']
        on = 212 + i * 24
        es.default_value = 0.0; es.keyframe_insert('default_value', frame=on)
        es.default_value = 8.0; es.keyframe_insert('default_value', frame=on + 6)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "corner_shot.blend"))

sc.render.image_settings.file_format = 'JPEG'
if MODE == "still":
    for f in (1, 170, 270):
        sc.frame_set(f)
        sc.render.filepath = f"{OUT}/still_f{f:03d}.jpg"
        bpy.ops.render.render(write_still=True)
elif MODE == "anim":
    os.makedirs(f"{OUT}/anim", exist_ok=True)
    sc.render.filepath = f"{OUT}/anim/f"
    bpy.ops.render.render(animation=True)
elif MODE == "passes":
    # material-override passes (Blender 5.1 compositor API unstable headless)
    os.makedirs(f"{OUT}/passes", exist_ok=True)
    sc.view_settings.view_transform = 'Standard'
    bg.inputs[1].default_value = 0.0
    for L0 in (sun, *plights):
        L0.data.energy = 0.0
        try: L0.data.animation_data_clear()
        except Exception: pass
    meshes = [o for o in sc.objects if o.type == 'MESH']
    orig = {o.name: [ms.material for ms in o.material_slots] for o in meshes}

    def em_mat(name, builder):
        m = bpy.data.materials.new(name); m.use_nodes = True
        nt2 = m.node_tree
        for n in list(nt2.nodes): nt2.nodes.remove(n)
        out = nt2.nodes.new('ShaderNodeOutputMaterial')
        em = nt2.nodes.new('ShaderNodeEmission')
        nt2.links.new(em.outputs[0], out.inputs[0])
        builder(nt2, em)
        return m

    def assign(fn):
        for o in meshes:
            m = fn(o)
            for ms in o.material_slots: ms.material = m
            if not o.material_slots: o.data.materials.append(m)

    def render_to(path, frame):
        sc.frame_set(frame)
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)

    # depth: camera view-z mapped 0..30m
    def b_depth(nt2, em):
        cam_d = nt2.nodes.new('ShaderNodeCameraData')
        mr = nt2.nodes.new('ShaderNodeMapRange')
        mr.inputs['From Max'].default_value = 30.0
        nt2.links.new(cam_d.outputs['View Z Depth'], mr.inputs['Value'])
        nt2.links.new(mr.outputs[0], em.inputs['Color'])
    # normal: world normal *0.5+0.5
    def b_normal(nt2, em):
        geo = nt2.nodes.new('ShaderNodeNewGeometry')
        vm = nt2.nodes.new('ShaderNodeVectorMath'); vm.operation = 'MULTIPLY_ADD'
        vm.inputs[1].default_value = (0.5, 0.5, 0.5); vm.inputs[2].default_value = (0.5, 0.5, 0.5)
        nt2.links.new(geo.outputs['Normal'], vm.inputs[0])
        nt2.links.new(vm.outputs[0], em.inputs['Color'])

    m_depth = em_mat('P_depth', b_depth)
    m_normal = em_mat('P_normal', b_normal)
    m_white = em_mat('P_white', lambda nt2, em: em.inputs['Color'].default_value.__setitem__(slice(0,3),(1,1,1)))
    m_blackp = em_mat('P_black', lambda nt2, em: em.inputs['Color'].default_value.__setitem__(slice(0,3),(0,0,0)))

    HERO = 270
    for f in (1, HERO, 300):
        assign(lambda o: m_depth)
        render_to(f"{OUT}/passes/depth_f{f:03d}.jpg", f)
        assign(lambda o: m_normal)
        render_to(f"{OUT}/passes/normal_f{f:03d}.jpg", f)
        for idx, nm in ((1, 'building'), (2, 'lamps'), (3, 'street'), (4, 'sign')):
            assign(lambda o, idx=idx: m_white if o.pass_index == idx else m_blackp)
            render_to(f"{OUT}/passes/mask_{nm}_f{f:03d}.jpg", f)
    # restore
    for o in meshes:
        for ms, m0 in zip(o.material_slots, orig[o.name]): ms.material = m0
print("CORNER DONE", MODE)
