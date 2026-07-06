c = op("/project1/relight")
c.op("lag_fluo").par.lag2 = 0.25
c.op("lev_L3_fluo").par.opacity.expr = "(0.6 + 0.4*abs(op(\"flick\")[0])) if (op(\"ctrl_fluo\")[0] > 0.012 and op(\"flick\")[0] > -0.45) else 0.0"
