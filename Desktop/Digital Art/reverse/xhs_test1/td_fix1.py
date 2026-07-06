c = op("/project1/relight")
c.op("lev_L1_practical").par.opacity.expr = "min(1.0, 0.6 + 1.2*op(\"ctrl_prac\")[0])"
c.op("lev_L2_soft").par.opacity.expr = "min(1.0, max(0.0, op(\"ctrl_soft\")[0]*5.0 - 0.27))"
c.op("lev_L3_fluo").par.opacity.expr = "min(1.0, max(0.0, (op(\"ctrl_fluo\")[0]-0.009)*81.0) * (1.0 if op(\"flick\")[0] > -0.2 else 0.0))"
c.op("lag_fluo").par.lag1 = 0.02
c.op("lag_fluo").par.lag2 = 0.06
c.op("lag_soft").par.lag1 = 0.06
c.op("lag_soft").par.lag2 = 0.2
