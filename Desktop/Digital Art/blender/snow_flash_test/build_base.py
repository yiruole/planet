"""Headless Blender: simplified snowy night scene, two lighting states.

Original procedural scene (snow slope + snow-laden conifer + ridge lights +
stars), rendered as two stills: state A (dim blue night) / state B (bright
front-lit snowfall state). Run:
  blender -b --python build_base.py -- <outdir>
"""
import bpy
import math
import random
import sys

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "/tmp"
random.seed(11)

# ---------- clean ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 96
sc.cycles.use_denoising = True
sc.render.resolution_x = 720
sc.render.resolution_y = 720
sc.render.film_transparent = False


def mat(name, base, rough=0.6, emit=None, emit_str=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*base, 1)
    b.inputs['Roughness'].default_value = rough
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = emit_str
    return m


snow_m = mat('snow', (0.92, 0.94, 1.0), rough=0.55)
dark_m = mat('ridge', (0.008, 0.010, 0.014), rough=0.9)
green_m = mat('spruce', (0.03, 0.10, 0.05), rough=0.8)
light_m = mat('village', (1, 1, 1), emit=(1.0, 0.55, 0.18), emit_str=14)
star_m = mat('star', (1, 1, 1), emit=(0.9, 0.95, 1.0), emit_str=60)


def add_displaced_plane(name, size, loc, material, disp_scale, strength, seed):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc)
    o = bpy.context.object
    o.name = name
    for _ in range(6):
        bpy.ops.object.modifier_add(type='SUBSURF') if False else None
    md = o.modifiers.new('sub', 'SUBSURF')
    md.subdivision_type = 'SIMPLE'
    md.levels = md.render_levels = 6
    tex = bpy.data.textures.new(name + '_t', 'CLOUDS')
    tex.noise_scale = disp_scale
    dm = o.modifiers.new('disp', 'DISPLACE')
    dm.texture = tex
    dm.strength = strength
    o.data.materials.append(material)
    return o


# ---------- terrain: foreground snow slope rising to the right ----------
ground = add_displaced_plane('ground', 30, (0, 0, 0), snow_m, 7.0, 0.85, 1)
ground.rotation_euler = (0, math.radians(-4), 0)   # slope up to the right

# ---------- background ridge (dark) ----------
ridge = add_displaced_plane('ridge', 60, (0, 28, 1.5), dark_m, 8, 3.0, 2)
ridge.rotation_euler = (math.radians(88), 0, 0)

# ---------- snow-laden spruce ----------
tree_x, tree_y = -1.6, 3.5
ztop = 3.2
# green cone core
bpy.ops.mesh.primitive_cone_add(radius1=1.0, depth=ztop,
                                location=(tree_x, tree_y, ztop / 2 + 0.3))
cone = bpy.context.object
cone.data.materials.append(green_m)
# snow clumps on the cone surface
for i in range(70):
    h = random.random() ** 0.8            # bias to bottom
    z = 0.4 + h * (ztop - 0.5)
    r_at = 1.0 * (1.0 - z / (ztop + 0.4)) + 0.05
    a = random.uniform(0, 2 * math.pi)
    rr = r_at * random.uniform(0.75, 1.0)
    s = random.uniform(0.14, 0.34) * (1.2 - 0.5 * h)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=s, segments=12, ring_count=8,
        location=(tree_x + math.cos(a) * rr, tree_y + math.sin(a) * rr,
                  z + 0.3 + s * 0.2))
    cl = bpy.context.object
    cl.scale = (1.0, 1.0, 0.45)
    cl.data.materials.append(snow_m)
# top snow cap
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(tree_x, tree_y, ztop + 0.42))
cap = bpy.context.object
cap.scale = (1, 1, 0.6)
cap.data.materials.append(snow_m)

# ---------- village lights along ridge ----------
for i in range(14):
    x = -12 + i * 1.7 + random.uniform(-0.4, 0.4)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, segments=8, ring_count=6,
                                         location=(x, 26, 2.2 + random.uniform(-0.2, 0.3)))
    bpy.context.object.data.materials.append(light_m)

# ---------- stars ----------
for i in range(70):
    a = random.uniform(-1.2, 1.2)
    el = random.uniform(0.15, 1.2)
    d = 55
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=random.uniform(0.02, 0.05), segments=6, ring_count=4,
        location=(math.sin(a) * d * math.cos(el), math.cos(a) * d * math.cos(el),
                  math.sin(el) * d))
    bpy.context.object.data.materials.append(star_m)

# ---------- world: night gradient ----------
world = bpy.data.worlds.new('night')
sc.world = world
world.use_nodes = True
nt = world.node_tree
bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
tc = nt.nodes.new('ShaderNodeTexCoord')
sep = nt.nodes.new('ShaderNodeSeparateXYZ')
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (0.030, 0.075, 0.240, 1)   # horizon navy
ramp.color_ramp.elements[1].position = 0.7
ramp.color_ramp.elements[1].color = (0.006, 0.015, 0.070, 1)   # zenith
nt.links.new(tc.outputs['Generated'], sep.inputs[0])
nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
bg.inputs['Strength'].default_value = 1.0

# ---------- camera ----------
bpy.ops.object.camera_add(location=(0.3, -7.5, 1.5),
                          rotation=(math.radians(84), 0, math.radians(-2)))
cam = bpy.context.object
cam.data.lens = 32
sc.camera = cam

# ---------- lights: moon (A) + front floods (B) ----------
bpy.ops.object.light_add(type='SUN', location=(10, -6, 20))
moon = bpy.context.object
moon.data.color = (0.55, 0.68, 1.0)
moon.rotation_euler = (math.radians(35), math.radians(25), 0)

bpy.ops.object.light_add(type='AREA', location=(1.5, -6.5, 4.5))
front = bpy.context.object
front.data.size = 8
front.data.color = (0.85, 0.92, 1.0)
front.rotation_euler = (math.radians(55), 0, math.radians(5))


# smooth shade everything organic
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name not in ():
        bpy.context.view_layer.objects.active = o
        for pg in o.data.polygons:
            pg.use_smooth = True


def render(path):
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


# ----- state A: dim blue night -----
moon.data.energy = 0.55
front.data.energy = 0
bg.inputs['Strength'].default_value = 0.85
render(OUT + '/base_A.png')

# ----- state