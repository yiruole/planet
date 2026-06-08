# Deploy v5: sharp-edged 3-layer cumulus + faster morphing

# 1. reload shader
with open('/Users/ruoleyi/Desktop/TDcloud/cloud_shader.frag', 'r', encoding='utf-8') as f:
    src = f.read()
dat = op('/project1/cloud_shader_dat')
dat.text = src

g = op('/project1/cloud_glsl')
g.par.pixeldat    = dat
g.par.resolutionw = 1280
g.par.resolutionh = 720

# 2. reload Script CHOP callbacks (faster baseline)
with open('/Users/ruoleyi/Desktop/TDcloud/cloud_growth_script.py', 'r', encoding='utf-8') as f:
    script_src = f.read()
script_dat = op('/project1/cloud_growth_dat')
if script_dat:
    script_dat.text = script_src
else:
    script_dat = op('/project1').create(textDAT, 'cloud_growth_dat')
    script_dat.text = script_src

gc = op('/project1/cloud_growth_chop')
if not gc:
    gc = op('/project1').create(scriptCHOP, 'cloud_growth_chop')
    gc.nodeX, gc.nodeY = -400, 400
    try: gc.par.callbacks = script_dat
    except: pass
    rms_op = op('/project1/cloud_analyze_rms')
    if rms_op: gc.inputConnectors[0].connect(rms_op)

try: gc.par.callbacks = script_dat
except: pass

# 3. uniforms
g.par.vec0name   = 'uTime'
g.par.vec0valuex.expr = "op('/project1/cloud_growth_chop')['cloud_time']"

g.par.vec1name   = 'uBeat'
g.par.vec1valuex.expr = "min(1.0, max(op('/project1/cloud_lag_beat')['chan1'], abs(op('/project1/cloud_lag_beat')['chan2'])) * 10.0)"

g.par.vec2name = ''

import time; time.sleep(0.4)
info = op('/project1/cloud_glsl_info')
err_lines = [l for l in info.text.splitlines() if 'ERROR' in l or 'error' in l.lower()]
print("Compile:", "ERRORS:\n" + "\n".join(err_lines) if err_lines else "OK")
gc.cook(force=True)
print("cloud_time:", gc['cloud_time'] if gc.numChans > 0 else "no chan")
print("uTime expr:", g.par.vec0valuex.expr)

result = "v5 deployed"
