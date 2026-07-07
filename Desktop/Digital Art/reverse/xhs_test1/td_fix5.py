c = op("/project1/relight")
for n in ("HALO_X", "HALO_BLUR", "HALO_LEV", "HALO_ADD"):
    if c.op(n): c.op(n).destroy()
hx = c.create(levelTOP, "HALO_X")
hx.inputConnectors[0].connect(c.op("mix_add"))
hx.par.blacklevel = 0.72
hx.nodeX, hx.nodeY = 1250, -450
hb = c.create(blurTOP, "HALO_BLUR")
hb.inputConnectors[0].connect(hx)
hb.par.size = 34
hb.nodeX, hb.nodeY = 1400, -450
hl = c.create(levelTOP, "HALO_LEV")
hl.inputConnectors[0].connect(hb)
hl.par.opacity = 0.5
hl.nodeX, hl.nodeY = 1550, -450
ha = c.create(compositeTOP, "HALO_ADD")
ha.par.operand = "add"
ha.inputConnectors[0].connect(c.op("mix_add"))
ha.inputConnectors[1].connect(hl)
ha.nodeX, ha.nodeY = 1250, -150
c.op("GRAIN").inputConnectors[0].connect(ha)
for n in ("L0_dark", "L1_practical", "L2_soft", "L3_fluo"):
    c.op(n).par.reloadpulse.pulse()
