import json, time
t = op("/local/time"); t.par.play = 0
c = op("/project1/relight")
data = {"prac": [], "soft": [], "fluo": [], "flick": []}
for f in range(1, 1261):
    t.frame = f
    for n in ("prac", "soft", "fluo"):
        data[n].append(round(float(c.op("ctrl_" + n)[0]), 6))
    data["flick"].append(round(float(c.op("flick")[0]), 4))
open("/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1/td_seq_stats.json", "w").write(json.dumps(data))
