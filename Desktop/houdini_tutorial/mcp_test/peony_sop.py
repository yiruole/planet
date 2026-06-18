import hou
import math
import random

node = hou.pwd()
geo = node.geometry()
geo.clear()

frame = hou.frame()
bloom_t = max(0.0, min(1.0, (frame - 1.0) / 119.0))

def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)

RU, RV = 14, 10

def petal_pts(scale):
    pts = []
    for iu in range(RU + 1):
        for iv in range(RV + 1):
            u = iu / RU
            v = iv / RV
            vc = v * 2.0 - 1.0
            # Width: 0 at base, widens to ~0.4 then tapers at tip
            w = math.sin(u * math.pi) ** 0.75
            px = vc * w * scale * 0.38
            py = u * scale
            # Cup: concave on inner face
            pz = -(1.0 - vc * vc) * scale * 0.045
            # Tip curls backward
            if u > 0.65:
                tip_t = (u - 0.65) / 0.35
                pz -= tip_t * tip_t * scale * 0.10
            # Ruffled edges (peony characteristic)
            if abs(vc) > 0.58:
                ef = (abs(vc) - 0.58) / 0.42
                pz += math.sin(u * 11.0 + vc * 7.2) * scale * 0.028 * ef * u * (1.0 - u * 0.35)
            pts.append((px, py, pz))
    return pts

# Geometry attributes
geo.addAttrib(hou.attribType.Point, "Cd", (1.0, 1.0, 1.0))
geo.addAttrib(hou.attribType.Point, "layer", 0)

# Layers: (num_petals, max_radius, petal_scale)
# Inner -> outer: more petals, wider, larger
layers = [
    (5,  0.00, 0.13),   # bud core
    (7,  0.09, 0.17),   # inner ring
    (10, 0.17, 0.22),   # middle ring
    (12, 0.25, 0.27),   # outer-middle
    (9,  0.33, 0.33),   # outer ring
]
NL = len(layers)
random.seed(42)

for li, (np_count, radius, ps) in enumerate(layers):
    lf = li / max(NL - 1, 1)

    # Inner petals open later (more delay for lf=0)
    delay = (1.0 - lf) * 0.28
    raw_t = max(0.0, bloom_t - delay) / max(1.0 - delay, 0.001)
    pb = ease(raw_t)

    # Radius expands as flower opens (petals push outward)
    anim_radius = radius * (0.25 + 0.75 * pb)

    # Tilt from vertical: outer petals droop more when fully open
    max_tilt = 18.0 + lf * 75.0
    tilt = pb * max_tilt
    cos_t = math.cos(math.radians(tilt))
    sin_t = math.sin(math.radians(tilt))

    # Color gradient: deep magenta center -> pale lavender-pink outer
    r = 0.45 + lf * 0.45
    g = 0.06 + lf * 0.52
    b = 0.35 + lf * 0.32
    col = (r, g, b)

    # Golden angle offset per layer for natural stagger
    ao = li * 0.618 * math.pi

    for pi_idx in range(np_count):
        az_rad = pi_idx * 2.0 * math.pi / np_count + ao + random.uniform(-0.07, 0.07)
        cos_a = math.cos(az_rad)
        sin_a = math.sin(az_rad)

        pts_local = petal_pts(ps)
        geo_pts = []

        for (lx, ly, lz) in pts_local:
            # 1. Tilt petal open: rotate around X axis
            x1 = lx
            y1 = ly * cos_t - lz * sin_t
            z1 = ly * sin_t + lz * cos_t
            # 2. Push out to ring radius
            z1 += anim_radius
            # 3. Rotate to azimuth position around Y axis
            x2 = x1 * cos_a + z1 * sin_a
            y2 = y1
            z2 = -x1 * sin_a + z1 * cos_a

            p = geo.createPoint()
            p.setPosition(hou.Vector3(x2, y2, z2))
            p.setAttribValue("Cd", col)
            p.setAttribValue("layer", li)
            geo_pts.append(p)

        # Build quad polygons
        for iu in range(RU):
            for iv in range(RV):
                i00 = iu * (RV + 1) + iv
                i10 = (iu + 1) * (RV + 1) + iv
                i01 = iu * (RV + 1) + iv + 1
                i11 = (iu + 1) * (RV + 1) + iv + 1
                poly = geo.createPolygon()
                for idx in [i00, i10, i11, i01]:
                    poly.addVertex(geo_pts[idx])
