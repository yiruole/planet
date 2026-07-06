import json
DIR = '/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1'
c = op('/project1/relight')
nz = c.create(noiseCHOP, 'flick')
nz.par.type = 'random'
nz.par.period = 0.12
nz.par.amp = 1.0
nz.par.seed = 7
nz.par.timeslice = True
nz.nodeX, nz.nodeY = 0, -420
plates = ['L0_dark', 'L1_practical', 'L2_soft', 'L3_fluo']
tops = []
for i, p in enumerate(plates):
    m = c.create(moviefileinTOP, p)
    m.par.file = DIR + '/plates/' + p + '.png'
    m.nodeX, m.nodeY = 700, -i * 130
    tops.append(m)
exprs = {
    'L1_practical': "min(1.0, 0.85 + 6.0*op('ctrl_prac')[0])",
    'L2_soft':      "min(1.0, max(0.0, op('ctrl_soft')[0]*14.0))",
    'L3_fluo':      "min(1.0, max(0.0, op('ctrl_fluo')[0]*60.0 - 0.05) * (1.0 if op('flick')[0] > 0.30 else 0.12))",
}
levs = []
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
with open(DIR + '/td_c2_log.json', 'w') as fp:
    json.dump({'ok': True, 'mix_inputs': [i.path for i in mix.inputs]}, fp)
