import json
log = {'errors': [], 'built': []}
DIR = '/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1'
c = op('/project1/relight')
# clear probes except audio
for o in list(c.children):
    if o.name != 'audio':
        o.destroy()

def E(fn, tag):
    try:
        r = fn(); log['built'].append(tag); return r
    except Exception as e:
        log['errors'].append([tag, str(e)]); return None

# ---------- CHOP: audio -> 3 bands -> rms -> lag -> null ----------
au = c.op('audio')
au.par.file = DIR + '/ref_audio.wav'
au.par.playmode = 'locked'
bands = {'prac': ('lowpass', 2.2), 'soft': ('bandpass', 2.9), 'fluo': ('highpass', 3.5)}  # cutofflog ~ 10^x Hz
x = 0
for name, (ftype, cut) in bands.items():
    f = c.create(audiofilterCHOP, 'filt_' + name); f.par.filter = ftype; f.par.cutofflog = cut
    a = c.create(analyzeCHOP, 'rms_' + name); a.par.function = 'rmspower'
    l = c.create(lagCHOP, 'lag_' + name)
    l.par.lag1 = 0.03 if name == 'fluo' else 0.08
    l.par.lag2 = 0.12 if name == 'fluo' else 0.35
    n = c.create(nullCHOP, 'ctrl_' + name)
    f.inputConnectors[0].connect(au)
    a.inputConnectors[0].connect(f)
    l.inputConnectors[0].connect(a)
    n.inputConnectors[0].connect(l)
    for o, i in ((f, 0), (a, 1), (l, 2), (n, 3)):
        o.nodeX, o.nodeY = i * 160, -x * 120
    x += 1

# sparse noise gate for fluorescent flicker
def mk_flick():
    nz = c.create(noiseCHOP, 'flick')
    nz.par.type = 'random'; nz.par.timeslice = True
    nz.par.period = 0.12; nz.par.amp = 1.0; nz.par.seed = 7
    nz.nodeX, nz.nodeY = 0, -420
    return nz
E(mk_flick, 'flick noise')

# ---------- TOP: plates -> level -> add composite ----------
plates = ['L0_dark', 'L1_practical', 'L2_soft', 'L3_fluo']
tops = []
for i, p in enumerate(plates):
    m = c.create(moviefileinTOP, p)
    m.par.file = DIR + '/plates/' + p + '.png'
    m.nodeX, m.nodeY = 700, -i * 130
    tops.append(m)
levs = []
exprs = {
    'L1_practical': "min(1.0, 0.85 + 0.5*op('ctrl_prac')[0])",
    'L2_soft':      "min(1.0, max(0.0, op('ctrl_soft')[0]*par_gain_soft))".replace('par_gain_soft', '6.0'),
    'L3_fluo':      "min(1.0, max(0.0, op('ctrl_fluo')[0]*10.0 - 0.06) * (1.0 if op('flick')[0] > 0.30 else 0.12))",
}
for i, p in enumerate(plates[1:], start=1):
    lv = c.create(levelTOP, 'lev_' + p)
    lv.inputConnectors[0].connect(tops[i])
    lv.par.opacity.expr = exprs[p]
    lv.nodeX, lv.nodeY = 900, -i * 130
    levs.append(lv)
mix = c.create(compositeTOP, 'mix_add')
mix.par.operand = 'add'
mix.inputConnectors[0].connect(tops[0])
for i, lv in enumerate(levs):
    mix.inputConnectors[i + 1].connect(lv)
mix.nodeX, mix.nodeY = 1100, -150

# ---------- post: grain + hsv ----------
def mk_post():
    gn = c.create(noiseTOP, 'GRAIN_SRC')
    gn.par.outputresolution = 'custom'
    gn.par.resolutionw = 720; gn.par.resolutionh = 560
    gn.par.mono = True
    gn.par.seed.expr = 'absTime.frame'
    gn.nodeX, gn.nodeY = 1100, -300
    gl = c.create(levelTOP, 'GRAIN_LEV'); gl.inputConnectors[0].connect(gn)
    gl.par.opacity = 0.06
    gl.nodeX, gl.nodeY = 1250, -300
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
    return h
h = E(mk_post, 'post chain')

outn = c.create(nullTOP, 'OUT')
outn.inputConnectors[0].connect(h if h else mix)
outn.nodeX, outn.nodeY = 1700, -150

rec = c.create(moviefileoutTOP, 'rec')
rec.inputConnectors[0].connect(outn)
rec.par.file = DIR + '/audio_relight_v1.mov'
rec.par.type = 'movie'; rec.par.videocodec = 'h264'; rec.par.fps = 30
if hasattr(rec.par, 'audiochop'): rec.par.audiochop = c.op('audio').path
rec.nodeX, rec.nodeY = 1850, -150

# timeline info
t = op('/local/time')
log['time_pars'] = [p.name for p in t.pars()] if t else 'no /local/time'
log['out_res'] = [outn.width, outn.height]
log['ctrl_sample'] = {n: float(c.op('ctrl_' + n)[0]) for n in bands}
with open(DIR + '/td_build_log.json', 'w') as fp:
    json.dump(log, fp, indent=1)
