c = op("/project1/relight")
l0 = c.op("lev_L0")
if not l0:
    l0 = c.create(levelTOP, "lev_L0")
    l0.inputConnectors[0].connect(c.op("L0_dark"))
    l0.nodeX, l0.nodeY = 900, 0
    c.op("mix_add").inputConnectors[0].connect(l0)
l0.par.opacity = 0.55
c.op("flick").par.period = 0.45
c.op("lag_fluo").par.lag1 = 0.02
c.op("lag_fluo").par.lag2 = 0.35
c.op("lev_L1_practical").par.opacity.expr = "min(1.0, 0.45 + 0.25*op(\"ctrl_prac\")[0])"
c.op("lev_L2_soft").par.opacity.expr = "min(0.85, max(0.0, op(\"ctrl_soft\")[0]*4.0 - 0.35))"
c.op("lev_L3_fluo").par.opacity.expr = "1.0 if (op(\"ctrl_fluo\")[0] > 0.0075 and op(\"flick\")[0] > -0.45) else 0.0"
