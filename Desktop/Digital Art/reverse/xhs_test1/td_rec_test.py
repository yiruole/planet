import json
t = op("/local/time"); t.par.play = 0
c = op("/project1/relight")
rec = c.op("rec")
rec.par.file = "/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1/rec_test.mov"
rec.par.record = 1
for f in range(1, 61):
    t.frame = f
    rec.par.addframe.pulse()
    rec.cook(force=True)
rec.par.record = 0
open("/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1/td_rec_log.json", "w").write(json.dumps({"done": "test60"}))
