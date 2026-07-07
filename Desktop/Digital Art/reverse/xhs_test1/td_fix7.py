c = op("/project1/relight")
DIR = "/Users/ruoleyi/Desktop/Digital Art/reverse/xhs_test1"
for n in ("L0_dark", "L1_practical", "L2_soft", "L3_fluo"):
    c.op(n).par.file = DIR + "/plates_v3/" + n + ".png"
    c.op(n).par.reloadpulse.pulse()
c.op("lev_L0").par.opacity = 0.42
for n in ("SOFT", "CHROMA_SRC", "CHROMA_LEV", "CHROMA", "TONE"):
    if c.op(n): c.op(n).destroy()
soft = c.create(blurTOP, "SOFT")
soft.par.size = 2.0
soft.inputConnectors[0].connect(c.op("HALO_ADD"))
soft.nodeX, soft.nodeY = 1330, -150
cs = c.create(noiseTOP, "CHROMA_SRC")
cs.par.outputresolution = "custom"
cs.par.resolutionw = 720; cs.par.resolutionh = 560
if hasattr(cs.par, "mono"): cs.par.mono = False
cs.par.seed.expr = "absTime.frame * 3.7"
cs.nodeX, cs.nodeY = 1330, -320
cl = c.create(levelTOP, "CHROMA_LEV")
cl.inputConnectors[0].connect(cs)
cl.par.opacity = 0.035
cl.nodeX, cl.nodeY = 1430, -320
ch = c.create(compositeTOP, "CHROMA")
ch.par.operand = "add"
ch.inputConnectors[0].connect(soft)
ch.inputConnectors[1].connect(cl)
ch.nodeX, ch.nodeY = 1430, -150
tone = c.create(levelTOP, "TONE")
tone.inputConnectors[0].connect(ch)
tone.par.outlow = 0.045
tone.par.inhigh = 0.96
tone.nodeX, tone.nodeY = 1500, -150
c.op("GRAIN").inputConnectors[0].connect(tone)
h = c.op("HSV_ADJUST")
h.par.hueoffset = 4
h.par.saturationmult = 0.88
