import json
DIR = '/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1'
t = op('/local/time')
t.par.play = 0
c = op('/project1/relight')
data = {'prac': [], 'soft': [], 'fluo': []}
for f in range(1, 1261, 10):
    t.frame = f
    for n in data:
        data[n].append(round(float(c.op('ctrl_' + n)[0]), 6))
with open(DIR + '/td_stats.json', 'w') as fp:
    json.dump(data, fp)
