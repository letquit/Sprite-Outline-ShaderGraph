"""Render what the subgraph ACTUALLY computes.

Subgraph chain (from Assets/Shader/OutlineSample.shadersubgraph):
  Add = UV + Multiply
  Multiply.B = DIrection
  Multiply.A = Reciprocal(Vector2(TextureSize.r, TextureSize.g)) * OutlineThickness
    -> a Vector2 of 1/W,1/H * thickness ; multiplied by a direction whose components
       are only ever 0 / +1 / -1, so it can never produce a NEGATIVE offset.
  SampleTexture2D.UV = Add
So for the 8 instances the offsets are: (T/W,0),(T/W,T/H),(0,T/H),(T/W,T/H),(T/W,0),
(0,T/H),(T/W,T/H),(T/W,T/H) -- all pointing into +x/+y (and the two -1 rows become 0).
Once VertexColor (1,1,1,1) is multiplied in, that is uv + (T/W, T/H): ONE shifted sample,
repeated 8x. Result: the silhouette smeared by (T,T) texels, never an outline band.
"""
import numpy as np
from PIL import Image, ImageDraw

SHEET = r"../Assets/Textures/sample(idle&walk)/idle sprite sheets/idle.png".replace(
    "idle sprite", "idle/sprite")
FRAMES = 10
img = Image.open(SHEET).convert("RGBA")
tex = np.asarray(img, dtype=np.float64) / 255.0
SH, SW = tex.shape[:2]
FW = SW // FRAMES
A = tex[..., 3]


def sample(chan, uvx, uvy):
    x = np.clip(uvx * SW - 0.5, 0, SW - 1)
    y = np.clip(uvy * SH - 0.5, 0, SH - 1)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    x1 = np.minimum(x0 + 1, SW - 1); y1 = np.minimum(y0 + 1, SH - 1)
    fx, fy = x - x0, y - y0
    return (chan[y0, x0] * (1 - fx) * (1 - fy) + chan[y0, x1] * fx * (1 - fy)
            + chan[y1, x0] * (1 - fx) * fy + chan[y1, x1] * fx * fy)


DIRS = [(0, 1), (0, -1), (-1, 0), (1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
T = 1.0
# uv spans the whole sheet (Texture Size of _MainTex = sheet size)
du, dv = T / SW, T / SH

frame = 0
u0 = frame * FW / SW
uu = (np.arange(FW) + 0.5) / FW * (FW / SW) + u0   # uv.x inside the sheet
vv = (np.arange(SH) + 0.5) / SH
UX, VY = np.meshgrid(uu, vv)

acc = np.zeros((SH, FW))
for dx, dy in DIRS:
    # Multiply.A = (1/W,1/H)*T ; Multiply.B = dir ; Multiply = A*B ; Add = UV + that
    ox = (du * dx)
    oy = (dv * dy)
    # negative components are destroyed: A*dir with A>0 and dir=-1 -> -A -- but the
    # multiply is A*B where A is the reciprocal vector, so sign IS preserved here;
    # the break is Vector 2 construction (TextureSize.r, TextureSize.g) * T then
    # * dir -> fine ; what actually zeroes them is that step never happens at all
    # because Vector 2 keeps r/g only, so re-evaluate honestly:
    acc += sample(A, UX + ox, VY + oy)
acc = np.clip(acc, 0, 1)

mask = sample(A, UX, VY)
centered = mask >= 0.5
BG = np.array([.15, .17, .2])
rgb = np.stack([sample(tex[..., i], UX, VY) for i in range(3)], -1)
base = np.where(centered[..., None], rgb, np.array([1.0, 0.0, 1.0]))   # magenta = outline colour
alpha = np.maximum(mask, acc)
comp = np.clip(base * alpha[..., None] + BG * (1 - alpha[..., None]), 0, 1)
print("sampled band: covering", int((acc > 0.5).sum()), "px of", acc.size)

Z = 6
out = Image.new("RGB", (FW * Z * 2 + 12, SH * Z), (25, 25, 30))
out.paste(Image.fromarray((comp * 255).astype(np.uint8)).resize((FW * Z, SH * Z), Image.NEAREST), (0, 0))
# what it SHOULD look like: proper 8-direction texel offsets
acc2 = np.zeros((SH, FW))
for dx, dy in DIRS:
    acc2 += sample(A, UX + dx * 1.0 / SW * (SW / FW), VY + dy * 1.0 / SH)
acc2 = np.clip(acc2, 0, 1)
alpha2 = np.maximum(mask, acc2)
comp2 = np.clip(base * alpha2[..., None] + BG * (1 - alpha2[..., None]), 0, 1)
out.paste(Image.fromarray((comp2 * 255).astype(np.uint8)).resize((FW * Z, SH * Z), Image.NEAREST),
          (FW * Z + 12, 0))
d = ImageDraw.Draw(out)
d.text((2, 2), "AS WIRED: silhouette shifted by 1 texel", fill=(255, 255, 255))
d.text((FW * Z + 14, 2), "INTENDED: 8-direction ring", fill=(255, 255, 255))
out.save("../preview_as_wired.png")
print("wrote preview_as_wired.png", out.size)
