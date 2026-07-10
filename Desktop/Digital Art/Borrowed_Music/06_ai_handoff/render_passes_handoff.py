#!/usr/bin/env python3
"""Render depth + category masks for each shot's conditioning frame, aligned
with prod/ RGB frames (same 640x360, same marker-bound cameras). Material
override method (Blender 5.1 headless-safe). EEVEE, fast.
Run: blender -b --python render_passes_handoff.py -- <tmpout> noop"""
import bpy, sys, os, math

BM = os.path.expanduser("~/Desktop/Digital Art/Borrowed_Music")
HD = f"{BM}/06_ai_handoff"

# build the production scene (MODE 'noop' skips its render branches)
code = open(f"{BM}/02_blender/build_production.py").read()
exec(compile(code, "production_scene", "exec"))

sc = bpy.context.scene
sc.view_settings.view_transform = 'Standard'
sc.render.resolution_x, sc.render.resolution_y = 640, 360

# silence world (star strength is node-driven: cut links, zero it)
wnt = sc.world.node_tree
wbg = next(n for n in wnt.nodes if n.type == 'BACKGROUND')
for lk in list(wnt.links):
    if lk.to_node == wbg:
        wnt.links.remove(lk)
wbg.inputs['Strength'].default_value = 0.0
wbg.inputs['Color'].default_value = (0, 0, 0, 1)
# kill all lights incl. keyframed ones
for o in sc.objects:
    if o.type == 'LIGHT':
        if o.data.animation_data:
            o.data.animation_data_clear()
        o.data.energy = 0.0

meshes = [o for o in sc.objects if o.type == 'MESH']

def em_mat(name, builder):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt2 = m.node_tree
    for n in list(nt2.nodes): nt2.nodes.remove(n)
    out = nt2.nodes.new('ShaderNodeOutputMaterial')
    em = nt2.nodes.new('ShaderNodeEmission')
    nt2.links.new(em.outputs[0], out.inputs[0])
    builder(nt2, em)
    return m

def flat(name, v):
    return em_mat(name, lambda nt2, em: em.inputs['Color'].default_value.__setitem__(slice(0, 3), (v, v, v)))

depth_maxes = {}
def b_depth(nt2, em):
    cam_d = nt2.nodes.new('ShaderNodeCameraData')
    mr = nt2.nodes.new('ShaderNodeMapRange'); mr.name = 'DRANGE'
    mr.inputs['From Max'].default_value = 30.0
    pw = nt2.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'
    pw.inputs[1].default_value = 0.5   # non-linear: near AND far readable
    inv = nt2.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0  # near = bright (convention noted in INDEX)
    nt2.links.new(cam_d.outputs['View Z Depth'], mr.inputs['Value'])
    nt2.links.new(mr.outputs[0], pw.inputs[0])
    nt2.links.new(pw.outputs[0], inv.inputs[1])
    nt2.links.new(inv.outputs[0], em.inputs['Color'])

m_depth = em_mat('P_depth', b_depth)
drange = m_depth.node_tree.nodes['DRANGE'].inputs['From Max']
m_white = flat('P_white', 1.0)
m_black = flat('P_black', 0.0)

def group_of(o):
    n = o.name
    if n.startswith(('int_', 'ext_')): return 'character'
    if n.startswith('film_'): return 'garment'
    if n.startswith(('rover', 'wheel', 'mast')) or n == 'anomaly': return 'props'
    return 'environment'

def assign(fn):
    for o in meshes:
        m = fn(o)
        if not o.material_slots:
            o.data.materials.append(m)
        else:
            for ms in o.material_slots: ms.material = m

def render_to(path, frame):
    sc.frame_set(frame)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)

sc.render.image_settings.file_format = 'PNG'
SHOTS = [(1, 1, 45.0), (2, 97, 8.0), (3, 193, 5.0), (4, 313, 6.0), (5, 505, 40.0), (6, 649, 35.0)]
for si, frame, dmax in SHOTS:
    d = f"{HD}/shot0{si}"
    drange.default_value = dmax
    assign(lambda o: m_depth)
    render_to(f"{d}/shot0{si}_depth.png", frame)
    for grp in ('character', 'environment', 'garment', 'props'):
        assign(lambda o, g=grp: m_white if group_of(o) == g else m_black)
        nm = {'character': 'character', 'environment': 'environment',
              'garment': 'music_garment', 'props': 'rover_props'}[grp]
        render_to(f"{d}/shot0{si}_masks/{nm}.png", frame)
print("PASSES DONE")
