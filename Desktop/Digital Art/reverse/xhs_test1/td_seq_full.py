import json, time
t = op("/local/time"); t.par.play = 0
c = op("/project1/relight")
o = c.op("OUT")
t0 = time.time()
for f in range(1, 1261):
    t.frame = f
    o.save("/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1/seq/f%05d.jpg" % f)
open("/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1/td_rec_log.json", "w").write(json.dumps({"secs": time.time() - t0, "frames": 1260}))
