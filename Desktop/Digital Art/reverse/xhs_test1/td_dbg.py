import json
t = op("/local/time"); t.par.play = 0; t.frame = 150
c = op("/project1/relight")
out = {}
for n in ("lev_L1_practical", "lev_L2_soft", "lev_L3_fluo"):
    p = c.op(n).par.opacity
    out[n] = {"expr": p.expr, "mode": str(p.mode), "val": float(p)}
ct = {}
for n in ("prac", "soft", "fluo"):
    ct[n] = float(c.op("ctrl_" + n)[0])
out["ctrl"] = ct
out["flick"] = float(c.op("flick")[0])
open("/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1/td_dbg.json", "w").write(json.dumps(out, indent=1))
