# Backrooms furniture-pile plates v2 — semantic assets + rigid-body settle + worn materials
# blender -b --python build_scene_v2.py -- <outdir>
import bpy, sys, math, random
from mathutils import Vector, Matrix

OUT = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else '/tmp/plates'
random.seed(11)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = 720, 560
try:
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    sc.render.engine = 'BLENDER_EEVEE'
if hasattr(sc, 'eevee'):
    if hasattr(sc.eevee, 'use_raytracing'): sc.eevee.use_raytracing = True
    if hasattr(sc.eevee, 'taa_render_samples'): sc.eevee.taa_render_samples = 128

# ---------------- materials with mottle + AO dirt ----------------
def worn_mat(name, base, rough=0.7, mottle=0.35, rough_var=0.2, metallic=0.0, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Metallic'].default_value = metallic
    if emit:
        bsdf.inputs['Emission Color'].default_value = (*emit, 1)
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = random.uniform(6, 14)
    cr = nt.nodes.new('ShaderNodeValToRGB')
    dark = tuple(c * (1 - mottle) for c in base)
    cr.color_ramp.elements[0].color = (*dark, 1)
    cr.color_ramp.elements[1].color = (*base, 1)
    nt.links.new(noise.outputs['Fac'], cr.inputs['Fac'])
    ao = nt.nodes.new('ShaderNodeAmbientOcclusion'); ao.inputs['Distance'].default_value = 0.6
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs['Factor'].default_value = 0.72
    nt.links.new(cr.outputs['Color'], mix.inputs[6])   # A
    # B = color * AO (crevice dirt)
    mult = nt.nodes.new('ShaderNodeMix'); mult.data_type = 'RGBA'; mult.blend_type = 'MULTIPLY'
    mult.inputs['Factor'].default_value = 0.85
    nt.links.new(cr.outputs['Color'], mult.inputs[6])
    nt.links.new(ao.outputs['Color'], mult.inputs[7])
    nt.links.new(mult.outputs[2], mix.inputs[7])
    nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])
    rn = nt.nodes.new('ShaderNodeTexNoise'); rn.inputs['Scale'].default_value = random.uniform(15, 30)
    rmap = nt.nodes.new('ShaderNodeMapRange')
    rmap.inputs['To Min'].default_value = max(0.05, rough - rough_var)
    rmap.inputs['To Max'].default_value = min(1.0, rough + rough_var)
    nt.links.new(rn.outputs['Fac'], rmap.inputs['Value'])
    nt.links.new(rmap.outputs['Result'], bsdf.inputs['Roughness'])
    bmp = nt.nodes.new('ShaderNodeBump'); bmp.inputs['Strength'].default_value = 0.12
    bn = nt.nodes.new('ShaderNodeTexNoise'); bn.inputs['Scale'].default_value = random.uniform(40, 90)
    nt.links.new(bn.outputs['Fac'], bmp.inputs['Height'])
    nt.links.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    if random.random() < 0.4 and 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.18
    return m

WOODS = [worn_mat('wood_%d' % i, c, 0.5, 0.45, rough_var=0.28)
         for i, c in enumerate([(0.11, 0.05, 0.022), (0.16, 0.08, 0.035), (0.07, 0.035, 0.018), (0.19, 0.10, 0.045)])]
FABRICS = [worn_mat('fab_%d' % i, c, 0.92, 0.3)
           for i, c in enumerate([(0.07, 0.05, 0.038), (0.09, 0.068, 0.045), (0.05, 0.042, 0.036)])]
LEATHER = worn_mat('leather', (0.09, 0.04, 0.02), 0.5, 0.4)
METAL = worn_mat('metal', (0.35, 0.33, 0.30), 0.35, 0.25, 0.25, metallic=0.8)
PLASTIC = worn_mat('plastic', (0.10, 0.10, 0.11), 0.42, 0.2)
PAPER = worn_mat('paper', (0.42, 0.38, 0.30), 0.85, 0.3)

def pick_wood(): return random.choice(WOODS)

# ---------------- primitive helpers (collected into one furniture object) ----------------
_parts = []
def P_box(size, loc, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.scale = size; _parts.append(o); return o
def P_cyl(r, d, loc, rot=(0, 0, 0), vts=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vts, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.object; _parts.append(o); return o
def P_cone(r1, r2, d, loc, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=r1, radius2=r2, depth=d, location=loc, rotation=rot)
    o = bpy.context.object; _parts.append(o); return o

def finish(name, mats):
    global _parts
    for o in _parts:
        o.data.materials.append(random.choice(mats) if isinstance(mats, list) else mats)
    ctx = bpy.context.copy()
    for o in bpy.context.selected_objects: o.select_set(False)
    for o in _parts: o.select_set(True)
    bpy.context.view_layer.objects.active = _parts[0]
    bpy.ops.object.join()
    ob = bpy.context.object; ob.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    bev = ob.modifiers.new('bev', 'BEVEL')
    bev.width = random.uniform(0.008, 0.018); bev.segments = 2; bev.angle_limit = math.radians(40)
    _parts = []
    return ob

# ---------------- furniture archetypes (origin near own center) ----------------
def chair():
    w = pick_wood()
    P_box((0.44, 0.44, 0.045), (0, 0, 0.45))                      # seat
    for k in range(5):                                            # curved slat back
        aa = (k - 2) * 0.16
        P_box((0.035, 0.085, 0.5), (-0.2 - 0.05 * abs(aa) * 2, aa * 0.44 / 0.8, 0.72), (0, 0, aa * 0.55))
    P_box((0.05, 0.05, 0.5), (-0.2, -0.19, 0.72))
    P_box((0.05, 0.05, 0.5), (-0.2, 0.19, 0.72))
    P_box((0.05, 0.44, 0.08), (-0.2, 0, 0.95))                    # top rail (frame w/ opening)
    for sx, sy in ((0.18, 0.18), (0.18, -0.18), (-0.18, 0.18), (-0.18, -0.18)):
        P_cyl(0.02, 0.45, (sx, sy, 0.22))
    return finish('chair', w)

def office_chair():
    P_box((0.48, 0.48, 0.09), (0, 0, 0.48))
    P_box((0.07, 0.45, 0.55), (-0.24, 0, 0.85), (0, math.radians(-8), 0))
    P_cyl(0.035, 0.35, (0, 0, 0.25))
    for i in range(5):
        a = i * 2 * math.pi / 5
        P_cyl(0.018, 0.3, (0.14 * math.cos(a), 0.14 * math.sin(a), 0.06), (0, math.radians(90), a))
    ob = finish('office_chair', [FABRICS[0], PLASTIC])
    return ob

def table():
    w = pick_wood()
    P_box((1.15, 0.68, 0.045), (0, 0, 0.71))
    for sx, sy in ((0.5, 0.28), (0.5, -0.28), (-0.5, 0.28), (-0.5, -0.28)):
        P_box((0.06, 0.06, 0.68), (sx, sy, 0.35))
    P_box((1.0, 0.05, 0.09), (0, 0.28, 0.63)); P_box((1.0, 0.05, 0.09), (0, -0.28, 0.63))
    return finish('table', w)

def armchair():
    f = random.choice([FABRICS[1], LEATHER])
    P_box((0.85, 0.8, 0.4), (0, 0, 0.25))
    P_box((0.16, 0.8, 0.35), (0.42, 0, 0.6)); P_box((0.16, 0.8, 0.35), (-0.42, 0, 0.6))
    P_box((0.8, 0.18, 0.55), (0, 0.36, 0.62), (math.radians(-8), 0, 0))
    P_box((0.66, 0.55, 0.14), (0, -0.05, 0.5))
    return finish('armchair', f)

def cabinet():
    w = pick_wood()
    P_box((0.52, 0.46, 0.92), (0, 0, 0.46))
    for i, dz in enumerate((0.18, 0.46, 0.74)):
        pull = 0.16 if i == 1 else 0.02
        P_box((0.46, 0.06, 0.24), (0, -0.26 - pull, dz))
        P_cyl(0.012, 0.1, (0, -0.31 - pull, dz), (math.radians(90), 0, 0))
    return finish('cabinet', w)

def lamp():
    P_cyl(0.14, 0.03, (0, 0, 0.015))
    P_cyl(0.015, 1.35, (0, 0, 0.7))
    P_cone(0.22, 0.09, 0.28, (0, 0, 1.45))
    return finish('lamp', [METAL, PAPER])

def plank():
    w = pick_wood()
    P_box((random.uniform(1.0, 1.6), random.uniform(0.12, 0.3), 0.035), (0, 0, 0.02))
    return finish('plank', w)

def stool():
    w = pick_wood()
    P_cyl(0.19, 0.04, (0, 0, 0.44), vts=16)
    for i in range(3):
        a = i * 2 * math.pi / 3
        P_cyl(0.02, 0.45, (0.13 * math.cos(a), 0.13 * math.sin(a), 0.22), (random.uniform(-0.15, 0.15), 0.12, a))
    return finish('stool', w)

def drawer():   # loose pulled-out drawer
    w = pick_wood()
    P_box((0.42, 0.3, 0.05), (0, 0, 0.03))
    P_box((0.42, 0.05, 0.16), (0, 0.15, 0.1)); P_box((0.42, 0.05, 0.16), (0, -0.15, 0.1))
    P_box((0.05, 0.3, 0.16), (0.2, 0, 0.1)); P_box((0.05, 0.3, 0.16), (-0.2, 0, 0.1))
    return finish('drawer', w)

ARCH = [chair, chair, chair, office_chair, table, armchair, cabinet, lamp, plank, plank, stool, drawer]

# ---------------- room ----------------
wall_m = worn_mat('wall', (0.33, 0.30, 0.16), 0.85, 0.4)
floor_m = worn_mat('floor', (0.095, 0.07, 0.048), 0.92, 0.5)
ceil_m = worn_mat('ceil', (0.42, 0.41, 0.36), 0.9, 0.45)
grid_m = worn_mat('grid', (0.24, 0.24, 0.22), 0.7, 0.2)
def box(name, size, loc, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.scale = size
    o.data.materials.append(m); return o
W, D, H = 14, 10, 3
floor = box('floor', (W, D, 0.1), (0, 0, -0.05), floor_m)
box('ceiling', (W, D, 0.1), (0, 0, H + 0.05), ceil_m)
box('wall_back', (W, 0.1, H), (0, D / 2, H / 2), wall_m)
box('wall_l', (0.1, D, H), (-W / 2, 0, H / 2), wall_m)
box('wall_r', (0.1, D, H), (W / 2, 0, H / 2), wall_m)
for gx in range(-6, 7, 2):
    box('bx%d' % gx, (0.06, D, 0.05), (gx, 0, H - 0.02), grid_m)
for gy in range(-4, 5, 2):
    box('by%d' % gy, (W, 0.06, 0.05), (0, gy, H - 0.02), grid_m)
box('door', (0.12, 1.1, 2.2), (-W / 2 + 0.07, -2.5, 1.1), worn_mat('door', (0.24, 0.26, 0.28), 0.8))
sign_m = worn_mat('sign', (0.4, 0.04, 0.04), 0.5, 0.2)
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.35, depth=0.04, location=(4.6, 3.6, 1.5), rotation=(math.pi / 2, 0, 0))
bpy.context.object.data.materials.append(sign_m)
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=1.5, location=(4.6, 3.62, 0.75))
bpy.context.object.data.materials.append(METAL)

# ---------------- fluorescent panels: per-panel variance ----------------
panel_base = (1.0, 0.97, 0.86)
panel_mats = []
for i in range(5):
    pm = bpy.data.materials.new('panel_%d' % i); pm.use_nodes = True
    b = next(n for n in pm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (0.75, 0.75, 0.7, 1)
    b.inputs['Roughness'].default_value = 0.35
    b.inputs['Emission Color'].default_value = (*panel_base, 1)
    panel_mats.append((pm, random.uniform(0.55, 1.35)))
dead_i = {(1, 1), (-5, -3), (3, -1)}
fluos = []
panel_objs = []
dead_m = bpy.data.materials.new('panel_dead'); dead_m.use_nodes = True
db = next(n for n in dead_m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
db.inputs['Base Color'].default_value = (0.28, 0.28, 0.26, 1)
db.inputs['Roughness'].default_value = 0.4
for px in (-5, -3, -1, 1, 3, 5):
    for py in (-3, -1, 1, 3):
        if (px, py) in dead_i:
            o = box('panel_%d_%d' % (px, py), (1.15, 0.55, 0.03), (px, py, H - 0.05), dead_m)
            continue
        pm, scale = random.choice(panel_mats)
        o = box('panel_%d_%d' % (px, py), (1.15, 0.55, 0.03), (px, py, H - 0.05), pm)
        panel_objs.append((pm, scale))
        if (px + 1) % 2 == 0 and py in (-3, 1) and (px, py) not in dead_i:
            bpy.ops.object.light_add(type='AREA', location=(px, py, H - 0.1))
            L = bpy.context.object; L.data.size = 1.1
            L.data.color = (1.0, 0.96, 0.82); L.data.energy = 0
            fluos.append((L, random.uniform(0.7, 1.25)))

# ---------------- build furniture, deterministic stacked placement ----------------
# gravity-plausible by construction: each piece rests on floor or on the current
# pile top at its xy; tilt increases when supported by pile (leaning/jammed look)
furn = []
placed = []   # (x, y, top_z, footprint_radius)
NP = 62
big = [armchair, armchair, cabinet, cabinet, table, table, table, armchair, cabinet, table]
order = big + [random.choice(ARCH) for _ in range(NP - len(big))]
for i in range(NP):
    f = order[i]()
    s = random.uniform(0.8, 1.15) * (0.7 if random.random() < 0.1 else 1.0)
    f.scale = (s, s, s)
    bpy.context.view_layer.update()
    d = f.dimensions
    rad = max(d.x, d.y) * 0.5 * 0.8
    ok = False
    for attempt in range(60):
        u = random.random()
        r = (2.15 if i < 10 else 1.95) * (u ** 0.55)            # center-dense -> mound
        a = random.uniform(0, 2 * math.pi)
        x, y = r * math.cos(a), r * math.sin(a) * 0.72
        support = 0.0
        for (px, py, pz, pr) in placed:
            if math.hypot(x - px, y - py) < (rad + pr) * 0.6:
                support = max(support, pz)
        limit = 2.7 * max(0.0, 1.0 - r / 3.4)   # pile must slope down outward
        if support <= limit:
            ok = True
            break
    if not ok:
        bpy.data.objects.remove(f, do_unlink=True)
        continue
    tilt = 0.30 if support < 0.05 else 0.85
    rx = random.uniform(-tilt, tilt)
    ry = random.uniform(-tilt, tilt)
    if support > 0.05 and random.random() < 0.25:
        rx += math.pi * random.choice((0.5, 1.0))   # sideways / upside-down pieces inside pile
    f.rotation_euler = (rx, ry, random.uniform(0, 6.28))
    bpy.context.view_layer.update()
    dz = f.dimensions.z
    sink = 0.2 * dz if support > 0.05 else 0.0     # jammed-in look, hides bbox gaps
    f.location = (x, y, support + dz * 0.5 - sink)
    top = support + dz * (0.9 if support < 0.05 else 0.75)
    placed.append((x, y, top, rad))
    furn.append(f)
    print('PLACE %s dims=(%.2f,%.2f,%.2f) support=%.2f z=%.2f top=%.2f' % (f.name, d.x, d.y, d.z, support, f.location.z, top))
print('PILE placed %d/%d, max top %.2f' % (len(furn), NP, max(p[2] for p in placed)))

# ---------------- floor clutter (posed, gravity-plausible by construction) ----------------
def clutter_shoe(loc, yaw):
    P_box((0.26, 0.1, 0.07), (0, 0, 0.035)); P_box((0.12, 0.1, 0.07), (0.07, 0, 0.1))
    ob = finish('shoe', LEATHER); ob.location = loc; ob.rotation_euler = (0, 0, yaw); return ob
def clutter_book(loc, yaw):
    P_box((0.24, 0.17, 0.035), (0, 0, 0.018))
    ob = finish('book', PAPER); ob.location = loc; ob.rotation_euler = (0, 0, yaw); return ob
def clutter_bottle(loc, yaw):
    P_cyl(0.045, 0.26, (0, 0, 0.045), (0, math.radians(90), 0)); ob = finish('bottle', PLASTIC)
    ob.location = loc; ob.rotation_euler = (0, 0, yaw); return ob
for i in range(9):
    a = random.uniform(0, 2 * math.pi)
    r = random.uniform(1.9, 3.4)
    random.choice([clutter_shoe, clutter_book, clutter_bottle])((r * math.cos(a), r * math.sin(a) * 0.7 - 0.5, 0), random.uniform(0, 6.28))

# ---------------- lights ----------------
bulb_m = bpy.data.materials.new('bulb'); bulb_m.use_nodes = True
bb = next(n for n in bulb_m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bb.inputs['Emission Color'].default_value = (1.0, 0.85, 0.6, 1)
bulb_pos = (-0.3, -1.35, 1.55)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, location=bulb_pos)
bulb = bpy.context.object; bulb.data.materials.append(bulb_m)
bpy.ops.object.light_add(type='POINT', location=(bulb_pos[0], bulb_pos[1] - 0.18, bulb_pos[2]))
Lprac = bpy.context.object; Lprac.data.color = (1.0, 0.75, 0.45)
Lprac.data.shadow_soft_size = 0.12; Lprac.data.energy = 0
bpy.ops.object.light_add(type='AREA', location=(0, 0, H - 0.15))
Lsoft = bpy.context.object; Lsoft.data.size = 4.5
Lsoft.data.color = (0.75, 0.82, 0.9); Lsoft.data.energy = 0

vol_m = bpy.data.materials.new('haze'); vol_m.use_nodes = True
vnt = vol_m.node_tree
for n in list(vnt.nodes):
    if n.type == 'BSDF_PRINCIPLED': vnt.nodes.remove(n)
pv = vnt.nodes.new('ShaderNodeVolumePrincipled')
pv.inputs['Density'].default_value = 0.012
pv.inputs['Anisotropy'].default_value = 0.25
out = next(n for n in vnt.nodes if n.type == 'OUTPUT_MATERIAL')
vnt.links.new(pv.outputs['Volume'], out.inputs['Volume'])
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.5))
hz = bpy.context.object; hz.name = 'haze'; hz.scale = (13.8, 9.8, 2.98)
hz.data.materials.append(vol_m)

sc.world = bpy.data.worlds.new('w'); sc.world.use_nodes = True
bg = next(n for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (0.06, 0.075, 0.09, 1)
bg.inputs['Strength'].default_value = 0.0

bpy.ops.object.camera_add(location=(0, -5.35, 1.02))
cam = bpy.context.object; sc.camera = cam
cam.data.lens = 26
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 5.2
cam.data.dof.aperture_fstop = 2.5
tgt = Vector((0, 0, 1.15))
z = (cam.location - tgt).normalized(); x = Vector((0, 0, 1)).cross(z).normalized(); y = z.cross(x)
cam.matrix_world = Matrix(((x.x, y.x, z.x, cam.location.x), (x.y, y.y, z.y, cam.location.y),
                           (x.z, y.z, z.z, cam.location.z), (0, 0, 0, 1)))

def set_emit(m, s):
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Emission Strength'].default_value = s
def all_off():
    Lprac.data.energy = 0; Lsoft.data.energy = 0
    for B in globals().get('bounces', []): B.data.energy = 0
    for L, k in fluos: L.data.energy = 0
    set_emit(bulb_m, 0)
    for pm, k in panel_mats: set_emit(pm, 0)
    bg.inputs['Strength'].default_value = 0.0
def render(p):
    sc.render.filepath = p; bpy.ops.render.render(write_still=True)

all_off(); bg.inputs['Strength'].default_value = 0.22
render(OUT + '/L0_dark.png')
all_off(); Lprac.data.energy = 160; set_emit(bulb_m, 60)
render(OUT + '/L1_practical.png')
all_off(); Lsoft.data.energy = 320
render(OUT + '/L2_soft.png')
bounces = []
for bx in (-6.5, 6.5):
    bpy.ops.object.light_add(type='AREA', location=(bx, 0, 1.8), rotation=(0, math.radians(90 if bx < 0 else -90), 0))
    B = bpy.context.object; B.data.size = 6.0
    B.data.color = (0.9, 0.92, 0.72); B.data.energy = 0
    bounces.append(B)
all_off()
for L, k in fluos: L.data.energy = 105 * k; L.data.color = (0.99, 1.0, 0.8)
for B in bounces: B.data.energy = 28
for i, (pm, k) in enumerate(panel_mats): set_emit(pm, 3.1 * k)
# dead panels: their material scale already tiny via per-object mapping is shared; approximate dead via mats list
render(OUT + '/L3_fluo.png')

bpy.ops.wm.save_as_mainfile(filepath=OUT + '/backrooms_v3.blend')
print('V2 PLATES DONE')
