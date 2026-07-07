#!/usr/bin/env python3
"""video1 MVP: 'memory collection' core mechanism — live face footage sliced into
vertical strips mounted on a 3D accordion (zigzag panels), slowly rotating/folding,
over a warm amber gradient. Processes the VIDEO (face stays alive), not a still."""
import os
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

BASE = os.path.expanduser("~/Desktop/Digital Art/AE/video1/results/mvp")
SRC, OUT = os.path.join(BASE, "src"), os.path.join(BASE, "frames")
W, H = 540, 960
N = 8                      # accordion panels
CROP = (115, 100, 445, 690)  # face region in 540x960 src (x0,y0,x1,y1)

def homography(src_pts, dst_pts):
    A = []
    for (x, y), (u, v) in zip(src_pts, dst_pts):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y, -u])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y, -v])
    _, _, Vt = np.linalg.svd(np.asarray(A))
    return Vt[-1].reshape(3, 3)

def project(P, f=1.9, cam_z=-3.6):
    # P: (n,3) world -> pixel coords
    X, Y, Z = P[:, 0], P[:, 1], P[:, 2] - cam_z
    u = f * X / Z * H * 0.5 + W * 0.5
    v = -f * Y / Z * H * 0.5 + H * 0.47
    return np.stack([u, v], 1), Z

def bg_gradient():
    top, bot = np.array([234, 182, 118]), np.array([168, 104, 46])
    t = np.linspace(0, 1, H)[:, None, None]
    g = (top * (1 - t) + bot * t) * np.ones((H, W, 3))
    # subtle vignette
    yy, xx = np.mgrid[0:H, 0:W]
    r = ((xx - W / 2) / W) ** 2 + ((yy - H * 0.45) / H) ** 2
    return (g * (1 - 0.35 * r / r.max())[:, :, None]).astype(np.float32)

BG = bg_gradient()
frames = sorted(os.listdir(SRC))
light = np.array([0.75, 0.2, -0.55]); light /= np.linalg.norm(light)

for fi, name in enumerate(frames):
    tex = np.asarray(Image.open(os.path.join(SRC, name))).astype(np.float32)
    tex = tex[CROP[1]:CROP[3], CROP[0]:CROP[2]]
    th, tw = tex.shape[:2]
    t = fi / 30.0
    fold = np.radians(36 + 12 * np.sin(t * 1.1))       # fold angle oscillates
    yaw = np.radians(-14 + 9 * np.sin(t * 0.7 + 1.2))  # global slow rotation
    aspect = th / tw
    L = 2.0 / N                                        # panel width in world units
    # accordion vertex chain (x advances, z zigzags)
    xs, zs = [0.0], [0.0]
    for i in range(N):
        xs.append(xs[-1] + L * np.cos(fold))
        zs.append(zs[-1] + (L * np.sin(fold)) * (1 if i % 2 == 0 else -1))
    xs = np.array(xs) - xs[-1] / 2
    zs = np.array(zs) - np.mean(zs)
    ytop, ybot = aspect * 1.0, -aspect * 1.0
    cy, sy = np.cos(yaw), np.sin(yaw)
    R = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])

    canvas = BG.copy()
    order = []
    for i in range(N):
        c = np.array([
            [xs[i], ytop, zs[i]], [xs[i + 1], ytop, zs[i + 1]],
            [xs[i + 1], ybot, zs[i + 1]], [xs[i], ybot, zs[i]]]) @ R.T
        uv, Z = project(c)
        order.append((Z.mean(), i, c, uv))
    order.sort(key=lambda o: -o[0])  # far panels first

    for _, i, c, uv in order:
        sw0, sw1 = tw * i / N, tw * (i + 1) / N
        src_pts = [(sw0, 0), (sw1, 0), (sw1, th), (sw0, th)]
        Hm = homography(src_pts, [tuple(p) for p in uv])
        Hi = np.linalg.inv(Hm)
        x0, y0 = np.floor(uv.min(0)).astype(int) - 1
        x1, y1 = np.ceil(uv.max(0)).astype(int) + 1
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, W), min(y1, H)
        if x1 <= x0 or y1 <= y0:
            continue
        gy, gx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        ones = np.ones_like(gx)
        q = Hi @ np.stack([gx.ravel(), gy.ravel(), ones.ravel()])
        sx, sy_ = q[0] / q[2], q[1] / q[2]
        inside = (sx >= sw0) & (sx < sw1 - 0.5) & (sy_ >= 0) & (sy_ < th - 0.5)
        # panel shading from facing direction
        n3 = np.cross(c[1] - c[0], c[3] - c[0]); n3 /= np.linalg.norm(n3)
        shade = 0.56 + 0.44 * max(0.0, float(np.dot(n3, light)))
        patch = canvas[y0:y1, x0:x1]
        coords = np.stack([sy_, sx])
        for ch in range(3):
            samp = map_coordinates(tex[:, :, ch], coords, order=1, mode="nearest")
            flat = patch[:, :, ch].ravel()
            flat[inside] = samp[inside] * shade
            patch[:, :, ch] = flat.reshape(patch.shape[:2])
        # bright fold edge line (catch-light on crease)
        canvas[y0:y1, x0:x1] = patch
    Image.fromarray(canvas.clip(0, 255).astype(np.uint8)).save(
        os.path.join(OUT, "f%04d.jpg" % fi), quality=92)
    if fi % 30 == 0:
        print("frame", fi, flush=True)
print("done", len(frames))
