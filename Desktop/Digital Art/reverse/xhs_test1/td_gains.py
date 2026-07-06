c = op("/project1/relight")
c.op("lev_L1_practical").par.opacity.expr = "min(1.0, 0.8 + 1.3*op(\"ctrl_prac\")[0])"
c.op("lev_L2_soft").par.opacity.expr = "min(1.0, max(0.0, op(\"ctrl_soft\")[0]*6.0 - 0.15))"
c.op("lev_L3_fluo").par.opacity.expr = "min(1.0, max(0.0, (op(\"ctrl_fluo\")[0]-0.012)*90.0) * (1.0 if op(\"flick\")[0] > 0.30 else 0.12))"
