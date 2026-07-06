import json
t = op("/local/time"); t.par.play = 0
c = op("/project1/relight")
rec = c.op("rec")
rec.par.file = "/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1/audio_relight_v1.mov"
rec.par.record = 1
for f in range(1, 1261):
    t.frame = f
    rec.par.addframe.pulse()
rec.par.record = 0
open("/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1/td_rec_log.json", "w").write(json.dumps({"done": True}))
