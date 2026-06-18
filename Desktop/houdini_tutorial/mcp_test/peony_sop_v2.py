import hou
import math
import random

node = hou.pwd()
geo = node.geometry()
geo.clear()

frame = hou.frame()
raw_t = max(0.0, min(1.0, (frame - 1.0) / 119.0))

# Non-uniform bloom: fast initial pop then slow organic unfurl
# Derivative: high at t=0 (quick snap), decays fast
def bloom_ease(t):
    t = max(0.0, min(1.0, float(t)))
    if t < 0.18:
        ratio = max(0.0, t / 0.18)
        return (ratio ** 0.45) * 0.42
    else:
        s = max(0.0, min(1.0, (t - 0.18) / 0.82))
        s_ease = 1.0 - ((1.0 - s) ** 2.8)
        return 0.42 + s_ease * 0.58

bloom_t = bloom_ease(raw_t)

RU, RV = 20, 14   # higher res for vein/ruffle detail

def noise1d(x, seed=0):
    # simple deterministic pseudo-noise
    v = math.sin(x * 127.1 + seed * 311.7) * 43758.5453
    return v - math.floor(v)

def fbm(x, octaves=4, seed=0):
    val = 0.0
    amp = 0.5
    freq = 1.0
    for i in range(octaves):
        val += (noise1d(x * freq, seed + i) * 2.0 - 1.0) * amp
        amp *= 0.5
        freq *= 2.1
    return val

def petal_pts(scale, layer_idx, petal_idx, total_petals, seed_base):
    rng = random.Random(seed_base + petal_idx * 17 + layer_idx * 53)
    pts = []

    # Per-petal personality variation
    width_var   = rng.uniform(0.88, 1.12)
    length_var  = rng.uniform(0.92, 1.08)
    cup_var     = rng.uniform(0.7, 1.3)
    ruffle_freq = rng.uniform(8.0, 14.0)
    ruffle_ph   = rng.uniform(0, math.pi * 2)
    vein_count  = rng.randint(7, 13)
    # Veins much deeper — visible as geometry ridges in render
    vein_depth  = rng.uniform(0.018, 0.035) * scale
    tip_twist   = rng.uniform(-0.08, 0.08) * scale

    for iu in range(RU + 1):
        for iv in range(RV + 1):
            u = iu / RU   # 0=base, 1=tip
            v = iv / RV   # 0=left, 1=right
            vc = v * 2.0 - 1.0   # -1 to +1

            # Width profile: narrow base, widest at 55%, tapers to tip
            w = max(0.0, math.sin(u * math.pi * 0.95)) ** 0.6 * width_var
            # Outer layers get wider petals
            w *= (1.0 + layer_idx * 0.08)

            px = vc * w * scale * 0.40
            py = u * scale * length_var

            # --- CUP / CONCAVE SURFACE ---
            # Petals curve inward (cupping), stronger for inner layers
            cup_strength = (0.05 - layer_idx * 0.008) * cup_var
            pz = -(1.0 - vc * vc) * scale * cup_strength * max(0, 1.0 - u * 0.5)

            # --- TIP CURL-BACK ---
            # The tip rolls backward (outward from center) — key peony feature
            if u > 0.62:
                tip_t = (u - 0.62) / 0.38
                # outer layers curl back more
                curl_amt = (0.05 + layer_idx * 0.035) * scale
                pz -= math.sin(tip_t * math.pi * 0.5) ** 1.5 * curl_amt
                # slight lateral twist at tip
                px += tip_twist * tip_t ** 2

            # --- EDGE RUFFLE (small waves along petal edge) ---
            edge_fade = max(0.0, (abs(vc) - 0.55) / 0.45)
            if edge_fade > 0:
                ruffle_amp = scale * 0.022 * edge_fade * u * (1.2 - u * 0.4)
                pz += math.sin(u * ruffle_freq + ruffle_ph) * ruffle_amp
                # micro-serrations on very edge (the tiny notches in reference)
                if edge_fade > 0.75 and u > 0.3:
                    micro = math.sin(u * 38.0 + vc * 15.0 + rng.uniform(0, 6)) * scale * 0.006 * edge_fade
                    pz += micro
                    px += math.cos(u * 42.0 + ruffle_ph) * scale * 0.004 * edge_fade

            # --- PARALLEL VEIN TEXTURE ---
            # Sharp ridges running base-to-tip, like real peony veins
            vein_u_freq = vein_count * 3.5
            # sin^16 makes very sharp narrow ridges (not broad bumps)
            vein_val = max(0.0, math.sin(vc * vein_u_freq + rng.uniform(0, 0.2))) ** 16
            pz += vein_val * vein_depth * u * (1.0 - u * 0.25)
            # Secondary finer veins between main ones
            fine_vein = max(0.0, math.sin(vc * vein_u_freq * 2.3 + 1.1)) ** 12
            pz += fine_vein * vein_depth * 0.4 * u
            # Longitudinal micro-crease along vein direction
            pz += math.sin(u * 18.0 + vc * 2.5) * scale * 0.005 * u

            # --- LARGE-SCALE PETAL WARP (organic surface variation) ---
            warp = fbm(u * 2.3 + vc * 1.1, seed=seed_base + petal_idx)
            pz += warp * scale * 0.012 * u * (1.0 - u)

            pts.append((px, py, pz))
    return pts

# Geometry attributes
geo.addAttrib(hou.attribType.Point, "Cd", (1.0, 1.0, 1.0))
geo.addAttrib(hou.attribType.Point, "layer", 0)

# Layers: tighter radii so petals overlap like shingles, not spaced rings
# (num_petals, base_radius, petal_scale)
layers = [
    (6,  0.00, 0.11),   # bud core
    (8,  0.04, 0.16),   # inner ring
    (11, 0.08, 0.22),   # mid-inner
    (13, 0.13, 0.28),   # mid-outer
    (10, 0.18, 0.35),   # outer ring
]
NL = len(layers)
random.seed(7)

for li, (np_count, radius, ps) in enumerate(layers):
    lf = li / max(NL - 1, 1)   # 0=inner, 1=outer

    # Outer petals open first (fast pop), inner follow slowly
    # delay: inner layers have MORE delay
    delay = (1.0 - lf) * 0.32
    layer_raw = max(0.0, raw_t - delay) / max(1.0 - delay, 0.001)
    pb = bloom_ease(layer_raw)

    # Radius: petals spread outward AND droop as they open
    anim_radius = radius * (0.20 + 0.80 * pb)

    # Tilt: outer petals droop more, but max ~68° so they never lie flat
    max_tilt = 8.0 + lf * 60.0
    tilt = pb * max_tilt
    cos_t = math.cos(math.radians(tilt))
    sin_t = math.sin(math.radians(tilt))

    # Color: deep magenta-purple core → pale lavender-pink outer
    r = 0.38 + lf * 0.48
    g = 0.04 + lf * 0.46
    b = 0.32 + lf * 0.35
    # darken undersides slightly (handled by Cd per-petal later)
    col = (r, g, b)

    # Golden angle + layer offset for natural stagger
    ao = li * 0.618033 * math.pi * 2 + li * 0.23

    for pi_idx in range(np_count):
        az_rad = pi_idx * 2.0 * math.pi / np_count + ao + random.uniform(-0.09, 0.09)
        cos_a = math.cos(az_rad)
        sin_a = math.sin(az_rad)

        # --- PER-PETAL BLOOM STAGGER ---
        # Each petal within a layer opens at a slightly different time and amount
        petal_delay_jitter = random.uniform(-0.06, 0.06)   # timing offset
        petal_tilt_jitter  = random.uniform(-8.0, 8.0)     # ±8° tilt variation
        petal_radius_jitter = random.uniform(0.88, 1.12)   # radius spread ±12%
        petal_height_jitter = random.uniform(-0.008, 0.008)  # subtle vertical offset

        p_layer_raw = max(0.0, min(1.0, layer_raw + petal_delay_jitter))
        pb_petal = bloom_ease(p_layer_raw)

        p_tilt = max(0.0, pb_petal * max_tilt + petal_tilt_jitter)
        p_cos_t = math.cos(math.radians(p_tilt))
        p_sin_t = math.sin(math.radians(p_tilt))
        p_radius = anim_radius * petal_radius_jitter

        seed_b = li * 1000 + pi_idx * 100
        pts_local = petal_pts(ps, li, pi_idx, np_count, seed_b)
        geo_pts = []

        for idx, (lx, ly, lz) in enumerate(pts_local):
            iv_idx = idx % (RV + 1)
            iu_idx = idx // (RV + 1)
            vc = (iv_idx / RV) * 2.0 - 1.0
            u = iu_idx / RU

            # 1. Tilt open — use per-petal tilt
            x1 = lx
            y1 = ly * p_cos_t - lz * p_sin_t
            z1 = ly * p_sin_t + lz * p_cos_t
            # 2. Push to ring radius — per-petal radius + height jitter
            z1 += p_radius
            y1 += petal_height_jitter
            # 3. Rotate to azimuth
            x2 =  x1 * cos_a + z1 * sin_a
            y2 =  y1
            z2 = -x1 * sin_a + z1 * cos_a

            p = geo.createPoint()
            p.setPosition(hou.Vector3(x2, y2, z2))

            # Per-point color variation: edges slightly darker/pinker
            edge_darken = max(0.0, (abs(vc) - 0.6) / 0.4) * 0.18
            tip_tint    = max(0.0, u - 0.7) / 0.3 * 0.12
            cr = max(0, col[0] - edge_darken * 0.3 + tip_tint * 0.15)
            cg = max(0, col[1] - edge_darken * 0.5 - tip_tint * 0.1)
            cb = max(0, col[2] - edge_darken * 0.1 + tip_tint * 0.05)
            p.setAttribValue("Cd", (cr, cg, cb))
            p.setAttribValue("layer", li)
            geo_pts.append(p)

        # Build quads
        for iu in range(RU):
            for iv in range(RV):
                i00 = iu * (RV + 1) + iv
                i10 = (iu + 1) * (RV + 1) + iv
                i01 = iu * (RV + 1) + iv + 1
                i11 = (iu + 1) * (RV + 1) + iv + 1
                poly = geo.createPolygon()
                for idx in [i00, i10, i11, i01]:
                    poly.addVertex(geo_pts[idx])
