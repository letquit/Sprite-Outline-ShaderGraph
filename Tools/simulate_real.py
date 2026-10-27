"""Simulate the outline shader on the REAL idle sprite sheet, and on one frame of it.

Two cases:
  A) as the graph is wired now: offsets in texels (1/texSize), uv = frame uv
  B) packed-atlas reality: uv is 0..1 inside the frame, so a "texel" is a frame texel
     but Texture Size returns the WHOLE sheet -> offsets shrink to 1/10 of a texel.
"""
import numpy as np
from PIL import Image, ImageDraw

SHEET = r"../Assets/Textures/sample(idle&walk)/idle/sprite sheets/idle.png"
DIRS = [(0, 1), (0, -1), (-1, 0), (1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]

img = Image.open(SHEET).convert("RGBA")
tex = np.asarray(img, dtype=np.float64) / 255.0
SH, SW = tex.shape[:2]
FRAMES = 10
FW = SW // FRAMES
print("sheet", SW, "x", SH, " frames:", FRAMES, "frame size", FW, "x", SH)


def sample(chan, xs, ys):
    x = np.clip(xs, 0, SW - 1)
    y = np.clip(ys, 0, SH - 1)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    x1 = np.minimum(x0 + 1, SW - 1); y1 = np.minimum(y0 + 1, SH - 1)
    fx, fy = x - x0, y - y0
    return (chan[y0, x0] * (1 - fx) * (1 - fy) + chan[y0, x1] * fx * (1 - fy)
            + chan[y1, x0] * (1 - fx) * fy + chan[y1, x1] * fx * fy)


def render(frame_px, thickness, texsize_for_uv):
    """frame_px: (y0, x0) of the frame; texsize_for_uv: what the Texture Size node returns."""
    y0, x0 = frame_px
    ys, xs = np.mgrid[y0:y0 + SH, x0:x0 + FW].astype(np.float64)
    # uv is 0..1 across the frame; offset = dir * thickness / texsize  (in uv)
    tw, th = texsize_for_uv
    alpha = tex[..., 3]
    acc = np.zeros((SH, FW))
    for dx, dy in DIRS:
        du = dx * thickness / tw
        dv = dy * thickness / th
        acc += sample(alpha, xs + du * FW, ys + dv * SH)
    band = np.clip(acc, 0, 1)
    centered = sample(alpha, xs, ys) >= 0.5
    rgb = tex[..., :3]
    r = sample(rgb[..., 0], xs, ys); g = sample(rgb[..., 1], xs, ys); b = sample(rgb[..., 2], xs, ys)
    base = np.where(centered[..., None], np.stack([r, g, b], -1), np.array([1.0, 0.0, 1.0]))
    out = np.maximum(sample(alpha, xs, ys), band)
    return base, out, band


BG = np.array([0.15, 0.17, 0.2])
panels = []
FRAME = 0
y0, x0 = 0, FRAME * FW

for label, thickness, ts in (("T=1, texSize=sheet (A)", 1.0, (SW, SH)),
                             ("T=1, texSize=frame (B)", 1.0, (FW, SH)),
                             ("T=4, texSize=frame", 4.0, (FW, SH)),
                             ("T=8, texSize=frame", 8.0, (FW, SH))):
    base, alpha, band = render((y0, x0), thickness, ts)
    a = alpha[..., None]
    comp = np.clip(base * a + BG * (1 - a), 0, 1)
    print(f"{label:26s} band px=1 -> {int((band > 0.5).sum()):5d}   band max={band.max():.2f}")
    panels.append((label, comp))

Z = 4
gap = 10
canvas = np.ones((SH * Z, (FW * Z + gap) * len(panels) - gap, 3)) * 0.05
for i, (label, comp) in enumerate(panels):
    big = np.asarray(Image.fromarray((comp * 255).astype(np.uint8)).resize((FW * Z, SH * Z), Image.NEAREST))
    canvas[:, i * (FW * Z + gap):i * (FW * Z + gap) + FW * Z] = big
img_out = Image.fromarray((canvas * 255).astype(np.uint8))
dr = ImageDraw.Draw(img_out)
for i, (label, _) in enumerate(panels):
    dr.text((i * (FW * Z + gap) + 2, 2), label, fill=(255, 255, 255))
img_out.save("../preview_real_sprite.png")
print("wrote preview_real_sprite.png", img_out.size)
