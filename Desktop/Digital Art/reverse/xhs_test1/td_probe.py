import json
base = op('/project1')
old = base.op('relight')
if old: old.destroy()
c = base.create(baseCOMP, 'relight')
c.nodeX, c.nodeY = 400, -400
probes = {
    'audio': c.create(audiofileinCHOP, 'audio'),
    'band': c.create(audiofilterCHOP, 'band_probe'),
    'an': c.create(analyzeCHOP, 'an_probe'),
    'lag': c.create(lagCHOP, 'lag_probe'),
    'lev': c.create(levelTOP, 'lev_probe'),
    'noise': c.create(noiseCHOP, 'noise_probe'),
    'compt': c.create(compositeTOP, 'comp_probe'),
    'mfo': c.create(moviefileoutTOP, 'mfo_probe'),
}
out = {}
for k, o in probes.items():
    d = {'pars': [p.name for p in o.pars()], 'menus': {}}
    for p in o.pars():
        if p.isMenu:
            try: d['menus'][p.name] = list(p.menuNames)
            except Exception: pass
    out[k] = d
with open('/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1/td_probe.json', 'w') as f:
    json.dump(out, f, indent=1)
