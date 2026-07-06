# Backrooms office light-group plates for TD audio-reactive mixing
# blender -b --python build_plates.py -- <outdir>
import bpy, sys, math, random
from mathutils import Vector, Matrix

OUT = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else '/tmp/plates'
random.seed(7)

# ---------- clean ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = 720, 560
try:
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    sc.render.engine = 'BLENDER_EEVEE'
if hasattr(sc, 'eevee') and hasattr(sc.eevee, 'use_raytracing'):
    sc.eevee.use_raytracing = True
if hasattr(sc.eevee, 'taa_render_samples'):
    sc.eevee.taa_render_samples = 160

def mat(name, base, rough=0.7, emit=None, emit_str=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*base, 1)
    bsdf.inputs['Roughness'].default_value = rough
    if emit:
        bsdf.inputs['Emission Color'].default_value = (*emit, 1)
        bsdf.inputs['Emission Strength'].default_value = emit_str
    return m

def box(name, size, loc, rot=(0,0,0), m=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = size
    if m: o.data.materials.append(m)
    return o

# ---------- room 14 x 10 x 3 ----------
wall_m  = mat('wall',  (0.30, 0.28, 0.19), 0.85)
floor_m = mat('floor', (0.10, 0.075, 0.05), 0.9)
ceil_m  = mat('ceil',  (0.55, 0.55, 0.50), 0.9)
W, D, H = 14, 10, 3
box('floor', (W, D, 0.1), (0, 0, -0.05), m=floor_m)
box('ceiling', (W, D, 0.1), (0, 0, H + 0.05), m=ceil_m)
box('wall_back', (W, 0.1, H), (0, D/2, H/2), m=wall_m)
box('wall_l', (0.1, D, H), (-W/2, 0, H/2), m=wall_m)
box('wall_r', (0.1, D, H), (W/2, 0, H/2), m=wall_m)
# ceiling T-grid bars (dark thin strips for tile look)
grid_m = mat('grid', (0.30, 0.30, 0.28), 0.8)
for gx in range(-6, 7, 2):
    box(f'bar_x{gx}', (0.06, D, 0.04), (gx, 0, H - 0.02), m=grid_m)
for gy in range(-4, 5, 2):
    box(f'bar_y{gy}', (W, 0.06, 0.04), (0, gy, H - 0.02), m=grid_m)

# door frame on left wall + stop sign right (silhouette landmarks)
door_m = mat('door', (0.28, 0.30, 0.33), 0.8)
box('door', (0.12, 1.1, 2.2), (-W/2 + 0.07, -2.5, 1.1), m=door_m)
sign_m = mat('sign', (0.45, 0.05, 0.05), 0.6)
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.35, depth=0.04,
    location=(4.6, 3.6, 1.5), rotation=(math.pi/2, 0, 0))
bpy.context.object.data.materials.append(sign_m)
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=1.5, location=(4.6, 3.62, 0.75))
bpy.context.object.data.materials.append(grid_m)

# ---------- junk pile proxy (center) ----------
wood1 = mat('wood1', (0.16, 0.08, 0.035), 0.75)
wood2 = mat('wood2', (0.21, 0.11, 0.05), 0.65)
dark  = mat('darkjunk', (0.07, 0.05, 0.035), 0.8)
mats = [wood1, wood2, dark]
pile = []
for layer in range(5):                      # stacked mound, radius shrinks with height
    r_lay = 2.3 - layer * 0.42
    z_lay = 0.28 + layer * 0.46
    n = max(3, 11 - layer * 2)
    for i in range(n):
        a = random.uniform(0, 2*math.pi)
        rr = random.uniform(0.15, r_lay)
        loc = (rr*math.cos(a), rr*math.sin(a)*0.8, z_lay + random.uniform(-0.1, 0.12))
        rot = tuple(random.uniform(-0.7, 0.7) for _ in range(3))
        s = (random.uniform(0.5, 1.3), random.uniform(0.35, 0.9), random.uniform(0.28, 0.6))
        pile.append(box(f'junk_{layer}_{i}', s, loc, rot, random.choice(mats)))
# chair-leg spikes poking out of silhouette
for i in range(14):
    a = random.uniform(0, 2*math.pi)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=random.uniform(0.7, 1.2),
        location=(random.uniform(-1.4, 1.4), random.uniform(-1.1, 1.1), random.uniform(1.4, 2.3)),
        rotation=(random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), 0))
    bpy.context.object.data.materials.append(dark)

# ---------- practical bulb inside pile ----------
bulb_m = mat('bulb', (1, 1, 1), 0.4, emit=(1.0, 0.85, 0.6), emit_str=0.0)  # strength set per layer
bulb_pos = (-0.35, -1.35, 1.72)   # front-top pocket, visible from camera
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=bulb_pos)
bulb = bpy.context.object; bulb.data.materials.append(bulb_m)
bpy.ops.object.light_add(type='POINT', location=(bulb_pos[0], bulb_pos[1] - 0.15, bulb_pos[2]))
Lprac = bpy.context.object; Lprac.data.color = (1.0, 0.75, 0.45)
Lprac.data.shadow_soft_size = 0.12; Lprac.data.energy = 0

# ---------- overhead soft (moon-pool) ----------
bpy.ops.object.light_add(type='AREA', location=(0, 0, H - 0.15))
Lsoft = bpy.context.object; Lsoft.data.size = 4.5
Lsoft.data.color = (0.75, 0.82, 0.9); Lsoft.data.energy = 0

# ---------- fluorescent grid: emissive panels + area lights ----------
panel_m = mat('panel', (0.9, 0.9, 0.85), 0.3, emit=(1.0, 0.98, 0.88), emit_str=0.0)
fluos = []
for px in (-5, -3, -1, 1, 3, 5):
    for py in (-3, -1, 1, 3):
        box(f'panel_{px}_{py}', (1.15, 0.55, 0.03), (px, py, H - 0.05), m=panel_m)
        if (px + 1) % 2 == 0 and py in (-3, 1):   # sparse real lights for cost
            bpy.ops.object.light_add(type='AREA', location=(px, py, H - 0.1))
            L = bpy.context.object; L.data.size = 1.1
            L.data.color = (1.0, 0.97, 0.85); L.data.energy = 0
            fluos.append(L)

# ---------- dim ambient world ----------
sc.world = bpy.data.worlds.new('w'); sc.world.use_nodes = True
bg = next(n for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (0.06, 0.075, 0.09, 1)
bg.inputs['Strength'].default_value = 0.0

# ---------- camera (eye level, slightly low, centered) ----------
bpy.ops.object.camera_add(location=(0, -6.4, 1.15))
cam = bpy.context.object; sc.camera = cam
cam.data.lens = 26
tgt = Vector((0, 0, 1.25))
z = (cam.location - tgt).normalized()
x = Vector((0, 0, 1)).cross(z).normalized()
y = z.cross(x)
cam.matrix_world = Matrix(((x.x, y.x, z.x, cam.location.x),
                           (x.y, y.y, z.y, cam.location.y),
                           (x.z, y.z, z.z, cam.location.z),
                           (0, 0, 0, 1)))

def render(path):
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)

def all_off():
    Lprac.data.energy = 0; Lsoft.data.energy = 0
    for L in fluos: L.data.energy = 0
    bulb_m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0
    panel_m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0
    bg.inputs['Strength'].default_value = 0.0

def set_emit(m, s):
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Emission Strength'].default_value = s

# L0 dark ambient base (AgX crushes darks -> brighter than intuition)
all_off(); bg.inputs['Strength'].default_value = 0.22
render(OUT + '/L0_dark.png')

# L1 practical bulb only
all_off(); Lprac.data.energy = 160; set_emit(bulb_m, 60)
render(OUT + '/L1_practical.png')

# L2 overhead soft only
all_off(); Lsoft.data.energy = 320
render(OUT + '/L2_soft.png')

# L3 fluorescent full
all_off()
for L in fluos: L.data.energy = 60
set_emit(panel_m, 2.2)
render(OUT + '/L3_fluo.png')

bpy.ops.wm.save_as_mainfile(filepath=OUT + '/backrooms_plates.blend')
print('PLATES DONE')
