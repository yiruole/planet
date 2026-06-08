# Script CHOP: audio-accumulated cloud time
# FAST: clouds always moving visibly, loud music = very fast morph

_state = {'cloud_time': 0.0}

def cook(scriptOp):
    rms_op = op('/project1/cloud_analyze_rms')
    try:
        rms = max(abs(float(rms_op['chan1'])), abs(float(rms_op['chan2'])))
    except Exception:
        rms = 0.0

    fps = 60.0
    try:
        r = float(project.cookRate)
        if r > 0: fps = r
    except Exception:
        pass
    dt = 1.0 / fps

    # baseline=0.8: at silence, cloud_time += 0.8/s
    #   shape at scale 0.85 shifts 0.8*0.60/0.85 = 0.56 puff-widths/s → always visible
    # TIME_SCALE=20: at rms=0.10 -> rate=2.8/s -> shifts 2.0 puffs/s (very fast)
    baseline   = 0.8
    TIME_SCALE = 20.0
    rate = baseline + rms * TIME_SCALE

    _state['cloud_time'] += rate * dt

    scriptOp.clear()
    c = scriptOp.appendChan('cloud_time')
    c[0] = _state['cloud_time']
