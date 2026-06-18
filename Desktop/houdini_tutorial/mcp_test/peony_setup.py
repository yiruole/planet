import hou

obj = hou.node('/obj')

# Clean up any previous attempt
for name in ['peony', 'cam_peony', 'light_key', 'light_fill', 'light_rim']:
    n = obj.node(name)
    if n:
        n.destroy()

# Create geometry container
geo_node = obj.createNode('geo', 'peony')
for c in geo_node.children():
    c.destroy()

# Load SOP animation code
with open('/tmp/peony_sop.py') as f:
    sop_code = f.read()

# Python SOP: regenerates geometry every frame
py_sop = geo_node.createNode('python', 'bloom')
py_sop.parm('python').set(sop_code)

# Normal SOP for smooth shading
normal_sop = geo_node.createNode('normal', 'normals')
normal_sop.setInput(0, py_sop)
normal_sop.setDisplayFlag(True)
normal_sop.setRenderFlag(True)
geo_node.layoutChildren()

# Frame range: 120 frames
try:
    hou.playbar.setFrameRange(1, 120)
except Exception:
    pass
hou.setFrame(1)

# Camera: close-up portrait angle, 80mm focal length
cam = obj.createNode('cam', 'cam_peony')
cam.parmTuple('t').set((0.04, 0.22, 1.08))
cam.parmTuple('r').set((-12.0, 2.0, 0.0))
try:
    cam.parm('focal').set(80.0)
except Exception:
    pass

# Key light: warm from upper right
key = obj.createNode('hlight', 'light_key')
key.parmTuple('t').set((1.2, 1.8, 0.8))
key.parm('light_intensity').set(3.0)
try:
    key.parmTuple('light_color').set((1.0, 0.95, 0.88))
except Exception:
    pass

# Fill light: cool from left
fill = obj.createNode('hlight', 'light_fill')
fill.parmTuple('t').set((-0.9, 0.8, 0.5))
fill.parm('light_intensity').set(0.7)
try:
    fill.parmTuple('light_color').set((0.75, 0.78, 1.0))
except Exception:
    pass

# Rim light: from behind for petal translucency
rim = obj.createNode('hlight', 'light_rim')
rim.parmTuple('t').set((0.0, 1.4, -1.0))
rim.parm('light_intensity').set(1.5)
try:
    rim.parmTuple('light_color').set((1.0, 0.88, 0.95))
except Exception:
    pass

obj.layoutChildren()

print("Peony scene ready!")
print("  Geo: /obj/peony")
print("  Camera: /obj/cam_peony")
print("  Frame range: 1-120")
print("  Hit play to see the bloom animation.")
