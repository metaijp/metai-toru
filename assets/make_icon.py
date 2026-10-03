"""Genera el logo de MetAI Toru (assets/icon.png) — flecha de descarga sobre degradado azul→violeta."""
import sys
from PIL import Image, ImageDraw

N, K = 1024, 2  # K = supersampling
M = N * K
b, v = (59, 130, 246), (139, 92, 246)

grad = Image.new("RGB", (M, M))
px = grad.load()
for y in range(M):
    for x in range(M):
        t = (x + y) / (2 * M)
        px[x, y] = tuple(int(b[i] + (v[i] - b[i]) * t) for i in range(3))
mask = Image.new("L", (M, M), 0)
ImageDraw.Draw(mask).rounded_rectangle((60 * K, 60 * K, M - 60 * K, M - 60 * K), radius=225 * K, fill=255)
img = Image.new("RGBA", (M, M), (0, 0, 0, 0))
img.paste(grad, (0, 0), mask)

layer = Image.new("RGBA", (M, M), (0, 0, 0, 0))
d = ImageDraw.Draw(layer)
s = lambda *a: [int(x * K) for x in a]

# brillo suave
d.ellipse(s(560, 20, 1000, 460), fill=(255, 255, 255, 40))
d.ellipse(s(40, 700, 360, 1020), fill=(147, 197, 253, 45))

# flecha de descarga (punta con esquinas redondeadas)
W = (255, 255, 255, 255)
d.rounded_rectangle(s(452, 230, 572, 520), radius=60 * K, fill=W)
head = s(350, 490, 674, 490, 512, 664)
d.polygon(head, fill=W)
d.line(head + head[:2], fill=W, width=int(56 * K), joint="curve")
for i in range(0, 6, 2):
    r = 28 * K
    d.ellipse((head[i] - r, head[i + 1] - r, head[i] + r, head[i + 1] + r), fill=W)
# bandeja
T = (255, 255, 255, 235)
d.line(s(290, 640, 290, 770, 734, 770, 734, 640), fill=T, width=int(56 * K), joint="curve")
for p in ((290, 640), (734, 640)):
    d.ellipse(s(p[0] - 28, p[1] - 28, p[0] + 28, p[1] + 28), fill=T)
# destello ✦
sx, sy, r = 790, 250, 70
d.polygon(s(sx, sy - r, sx + r * .28, sy - r * .28, sx + r, sy, sx + r * .28, sy + r * .28,
            sx, sy + r, sx - r * .28, sy + r * .28, sx - r, sy, sx - r * .28, sy - r * .28), fill=(255, 255, 255, 235))

clip = Image.new("RGBA", (M, M), (0, 0, 0, 0))
clip.paste(layer, (0, 0), mask)  # recorta decoración al cuadrado redondeado
img = Image.alpha_composite(img, clip).resize((N, N), Image.LANCZOS)
img.save(sys.argv[1])
