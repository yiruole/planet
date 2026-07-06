import json
DIR = '/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1'
c = op('/project1/relight')
mix = c.op('mix_add')
log = {'errors': []}
gn = c.create(noiseTOP, 'GRAIN_SRC')
gn.par.outputresolution = 'custom'
gn.par.resolutionw = 720
gn.par.resolutionh = 560
if hasattr(gn.par, 'mono'): gn.par.mono = True
gn.par.seed.expr = 'absTime.frame'
gn.nodeX, gn.nodeY = 1100, -320
gl = c.create(levelTOP, 'GRAIN_LEV')
gl.inputConnectors[0].connect(gn)
gl.par.opacity = 0.06
gl.nodeX, gl.nodeY = 1250, -320
g = c.create(compositeTOP, 'GRAIN')
g.par.operand = 'add'
g.inputConnectors[0].connect(mix)
g.inputConnectors[1].connect(gl)
g.nodeX, g.nodeY = 1400, -150
h = c.create(hsvadjustTOP, 'HSV_ADJUST')
h.inputConnectors[0].connect(g)
for pn, v in (('saturationmult', 0.85), ('valuemult', 0.95)):
    if hasattr(h.par, pn): setattr(h.par, pn, v)
    else: log['errors'].append(['hsv par missing', pn])
h.nodeX, h.nodeY = 1550, -150
outn = c.create(nullTOP, 'OUT')
outn.inputConnectors[0].connect(h)
outn.nodeX, outn.nodeY = 1700, -150
rec = c.create(moviefileoutTOP, 'rec')
rec.inputConnectors[0].connect(outn)
rec.par.file = DIR + '/audio_relight_v1.mov'
rec.par.type = 'movie'
rec.par.videocodec = 'h264'
rec.par.fps = 30
if hasattr(rec.par, 'audiochop'): rec.par.audiochop = 'audio'
rec.nodeX, rec.nodeY = 1850, -150
log['hsv_pars'] = [p.name for p in h.pars() if 'sat' in p.name or 'val' in p.name or 'hue' in p.name]
log['ok'] = True
with open(DIR + '/td_c3_log.json', 'w') as fp:
    json.dump(log, fp)
