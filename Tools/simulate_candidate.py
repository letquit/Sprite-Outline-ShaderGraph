"""Render candidate A correctly: pixels count must be in FRAME space.

The sprite's mesh uv is 0..1 across the *frame*, and _MainTex is the whole sheet, so
uv*sheetSize lands in sheet pixels; an offset of dir*T in uv-pixels has to be applied
in the frame's pixel grid (T frame-texels = T pixels of the frame), then converted back.
"""
import numpy as np
from PIL import Image, ImageDraw

SHEET = "../Assets/Textures/sample(idle&walk)/idle/sprite sheets/idle.png"
FRAMES = 10
img = Image.open(SHEET).convert("RGBA")
tex = np.asarray(img, dtype=np.float64) / 255.0
SH, SW = tex.shape[:2]
FW = SW // FRAMES
A = tex[..., 3]
DIRS = [(0, 1), (0, -1), (-1, 0), (1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]


def bilinear(chan, x, y):
    x = np.clip(x, 0, SW - 1); y = np.clip(y, 0, SH - 1)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    x1 = np.minimum(x0 + 1, SW - 1); y1 = np.minimum(y0 + 1, SH - 1)
    fx, fy = x - x0, y - y0
    return (chan[y0, x0] * (1 - fx) * (1 - fy) + chan[y0, x1] * fx * (1 - fy)
            + chan[y1, x0] * (1 - fx) * fy + chan[y1, x1] * fx * fy)


frame = 0
gx = np.arange(FW) + 0.5          # frame pixel grid
gy = np.arange(SH) + 0.5
GX, GY = np.meshgrid(gx, gy)
PX, PY = GX + frame * FW, GY      # same points in sheet pixels

BG = np.array([.15, .17, .2])

panels = []
for label, scale in (("T=1 frame-texel (46/55)", 1.0), ("T=2", 2.0), ("T=3", 3.0)):
    band = np.zeros((SH, FW))
    for dx, dy in DIRS:
        band += bilinear(A, PX + dx * scale, PY + dy * scale)
    band = np.clip(band, 0, 1)
    mask = bilinear(A, PX, PY)
    base = np.where((mask >= 0.5)[..., None],
                    np.stack([bilinear(tex[..., i], PX, PY) for i in range(3)], -1),
                    np.zeros(3))
    alpha = np.maximum(mask, band)
    comp = np.clip(base * alpha[..., None] + BG * (1 - alpha[..., None]), 0, 1)
    panels.append((label, comp))

Z = 7
gap = 8
W = (FW * Z + gap) * len(panels)
out = Image.new("RGB", (W, SH * Z + 14), (25, 25, 30))
for i, (label, comp) in enumerate(panels):
    tile = Image.fromarray((comp * 255).astype(np.uint8)).resize((FW * Z, SH * Z), Image.NEAREST)
    out.paste(tile, (i * (FW * Z + gap), 14))
d = ImageDraw.Draw(out)
for i, (label, _) in enumerate(panels):
    d.text((i * (FW * Z + gap) + 2, 2), label, fill=(255, 255, 255))
out.save("../preview_candidate.png")
print("wrote preview_candidate.png", out.size)
