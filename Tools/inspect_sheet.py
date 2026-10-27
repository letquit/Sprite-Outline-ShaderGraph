"""What does the outline shader actually do on the real sprite sheet?

Chain (per frame): uv(0..1 in the frame) + dir * thickness / texSize -> sample idle.png
alphaframe = sum of 8 samples, saturated  -> the band
"""
import numpy as np
from PIL import Image, ImageDraw

SHEET = r"../Assets/Textures/sample(idle&walk)/idle/sprite sheets/idle.png"
img = Image.open(SHEET)
print("sheet:", img.size, img.mode)
tex = np.asarray(img.convert("RGBA"), dtype=np.float64) / 255.0
print("alpha unique stats: min/mean/max", tex[..., 3].min(), tex[..., 3].mean(), tex[..., 3].max())
print("fraction of pixels fully transparent:", float((tex[..., 3] < 0.01).mean()))
print("fraction fully opaque:", float((tex[..., 3] > 0.99).mean()))

"""
"""
