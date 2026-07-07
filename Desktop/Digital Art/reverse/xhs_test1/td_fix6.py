c = op("/project1/relight")
c.op("lev_L3_fluo").par.opacity.expr = "(0.6 + 0.4*abs(op(\"flick\")[0])) if (op(\"ctrl_fluo\")[0] > 0.010 and op(\"flick\")[0] > -0.55) else 0.0"
