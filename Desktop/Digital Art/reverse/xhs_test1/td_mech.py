import json
DIR = '/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1'
t = op('/local/time')
t.par.play = 0
t.par.end = 1300
t.par.rangeend = 1300
c = op('/project1/relight')
vals = {}
for f in (150, 369, 495, 615, 696, 900):
    t.frame = f
    ov = {}
    for n in ('prac', 'soft', 'fluo'):
        ov[n] = float(c.op('ctrl_' + n)[0])
    ov['flick'] = float(c.op('flick')[0])
    ov['lev_fluo_opacity'] = float(c.op('lev_L3_fluo').par.opacity)
    vals[f] = ov
    c.op('OUT').save(DIR + '/mech_f%04d.jpg' % f)
with open(DIR + '/td_mech_log.json', 'w') as fp:
    json.dump(vals, fp, indent=1)
