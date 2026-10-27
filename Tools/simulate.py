"""CPU simulation of PixelOutline.shadergraph math, to preview before/after in Unity.

before = today's graph: SurfaceDescription.Alpha is unconnected -> 1.0 everywhere
after  = patched graph:  Alpha = saturate(max(texA(uv), sum of 8 offset samples))
"""
import numpy as np
from PIL import Image, ImageDraw

W = H = 96
THICKNESS = 2.0
OUTLINE = (0.05, 0.05, 0.08)
BODY = (0.89, 0.55, 0.36)
BG = (0.86, 0.89, 0.93)

# ---- synthetic sprite: alpha mask + colour
mask_img = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(mask_img)
d.ellipse([34, 12, 62, 40], fill=255)            # head
d.rounded_rectangle([28, 36, 68, 84], 10, fill=255)  # body
d.ellipse([14, 44, 28, 58], fill=255)            # arm
texA = np.asarray(mask_img, dtype=np.float64) / 255.0

col_img = Image.new('RGB', (W, H), tuple(int(c * 255) for c in BODY))
texRGB = np.asarray(col_img, dtype=np.float64) / 255.0

DIRS = [(0, 1), (0, -1), (-1, 0), (1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]  # CORNERS_ON


def sample(chan, dx, dy):
    """bilinear sample of chan at uv + (dx, dy) texels, like the Texture2D node."""
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
    x = np.clip(xs + dx, 0, W - 1)
    y = np.clip(ys + dy, 0, H - 1)
    x0 = np.floor(x).astype(int)
    y0 = np.floor(y).astype(int)
    x1 = np.minimum(x0 + 1, W - 1)
    y1 = np.minimum(y0 + 1, H - 1)
    fx, fy = x - x0, y - y0
    return (chan[y0, x0] * (1 - fx) * (1 - fy) + chan[y0, x1] * fx * (1 - fy)
            + chan[y1, x0] * (1 - fx) * fy + chan[y1, x1] * fx * fy)


acc = np.zeros((H, W))
for dx, dy in DIRS:
    acc += sample(texA, dx * THICKNESS, dy * THICKNESS)
outline_mask = np.clip(acc, 0.0, 1.0)          # Saturate

centered = texA >= 0.5                          # Comparison node, B = 0.5
base = np.where(centered[..., None], texRGB, np.array(OUTLINE))  # Branch


def composite(alpha):
    a = alpha[..., None]
    return np.clip(base * a + np.array(BG) * (1 - a), 0, 1)


before = composite(np.ones((H, W)))                        # broken: alpha forced to 1
after = composite(np.maximum(texA, outline_mask))          # patched: max(texA, mask)

gap = 16
canvas = np.ones((H + 24, W * 2 + gap, 3)) * 0.99
canvas[:H, :W] = before
canvas[:H, W + gap:] = after
img = Image.fromarray((canvas * 255).astype(np.uint8)).resize(
    ((W * 2 + gap) * 3, (H + 24) * 3), Image.NEAREST)
dr = ImageDraw.Draw(img)
dr.text((6, H * 3 + 6), "BEFORE: Alpha=1 -> whole rect filled", fill=(20, 20, 20))
dr.text(((W + gap) * 3 + 6, H * 3 + 6), "AFTER: Alpha=max(texA,mask) -> outline", fill=(20, 20, 20))
img.save('../preview_outline.png')
print('wrote preview_outline.png', img.size)
print('alpha outside the band (should be 0):', float(np.max(after_band := np.maximum(texA, outline_mask)[texA < 0.02])))
