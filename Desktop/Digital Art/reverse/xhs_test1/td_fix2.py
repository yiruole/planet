c = op("/project1/relight")
c.op("lev_L1_practical").par.opacity.expr = "min(1.0, 0.62 + 0.5*op(\"ctrl_prac\")[0])"
c.op("lev_L3_fluo").par.opacity.expr = "min(1.0, max(0.0, (op(\"ctrl_fluo\")[0]-0.007)*95.0) * (1.0 if op(\"flick\")[0] > -0.5 else 0.0))"
c.op("lag_prac").par.lag2 = 0.15
c.op("lag_soft").par.lag2 = 0.1
