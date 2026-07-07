c = op("/project1/relight")
c.op("TONE").par.outlow = 0.03
for n in ("L0_dark", "L1_practical", "L2_soft", "L3_fluo"):
    c.op(n).par.reloadpulse.pulse()
