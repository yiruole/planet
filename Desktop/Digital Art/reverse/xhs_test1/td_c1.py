import json
DIR = '/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1'
base = op('/project1')
old = base.op('relight')
if old: old.destroy()
c = base.create(baseCOMP, 'relight')
c.nodeX, c.nodeY = 400, -400
au = c.create(audiofileinCHOP, 'audio')
au.par.file = DIR + '/ref_audio.wav'
au.par.playmode = 'locked'
bands = {'prac': ('lowpass', 2.2), 'soft': ('bandpass', 2.9), 'fluo': ('highpass', 3.5)}
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
t = op('/local/time')
with open(DIR + '/td_c1_log.json', 'w') as fp:
    json.dump({'ok': True, 'time_pars': [p.name for p in t.pars()] if t else None}, fp)
