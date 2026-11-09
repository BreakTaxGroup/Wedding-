"""Prepara las capas del sobre provisional a partir de la foto de referencia.

Mientras llega la imagen definitiva de Higgsfield, usa la foto del sobre de papel artesanal:
  - borra el nombre impreso (cada invitado ve el suyo, escrito en vivo),
  - cambia el monograma del sello por las iniciales de los novios,
  - separa el sello en dos mitades por una grieta, para la animación de ruptura.

Uso: python3 tools/prep_sobre.py FOTO FUENTE_SERIF SALIDA [--iniciales "I&H"]
Salida: sobre.jpg (sin nombre ni sello), sello.png, sello-a.png, sello-b.png, sello-sombra.png, sobre.json
"""
import argparse, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("foto"); ap.add_argument("fuente"); ap.add_argument("salida")
ap.add_argument("--iniciales", default="I&H")
a = ap.parse_args()

img = cv2.imread(a.foto).astype(np.float32)
H, W = img.shape[:2]
gray = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
rng = np.random.default_rng(3)

def pmask(pts):
    m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [np.int32(pts)], 255); return m

def grain_from(src, mask, shift, k=1.0):
    hf = src - cv2.GaussianBlur(src, (0, 0), 2.0)
    hf = cv2.warpAffine(hf, np.float32([[1, 0, -shift[0]], [0, 1, -shift[1]]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    return hf * cv2.GaussianBlur(mask.astype(np.float32) / 255, (0, 0), 1.5)[..., None] * k

# ---------- 1. borrar el nombre ----------
name_poly = [(835, 700), (1312, 588), (1312, 678), (835, 790)]
bg = cv2.medianBlur(gray.astype(np.uint8), 31).astype(np.float32)
zone = pmask(name_poly) > 0
strong = (((bg - gray) > 12) & zone).astype(np.uint8) * 255
near = cv2.dilate(strong, np.ones((3, 3), np.uint8), iterations=5) > 0
ink = ((((bg - gray) > 5) & zone & near) | (strong > 0)).astype(np.uint8) * 255
ink = cv2.dilate(ink, np.ones((3, 3), np.uint8), iterations=3)
clean = cv2.inpaint(img.astype(np.uint8), ink, 5, cv2.INPAINT_TELEA).astype(np.float32)
clean += grain_from(img, ink, (0, -95), 0.9)

# ---------- 2. sello: máscara de la cera ----------
sx0, sy0, sx1, sy1 = 680, 400, 910, 630
sub = gray[sy0:sy1, sx0:sx1]
m = (sub < 128).astype(np.uint8) * 255
ell = lambda k: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, ell(15)); m = cv2.morphologyEx(m, cv2.MORPH_OPEN, ell(11))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
m = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8) * 255
cn, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
m = np.zeros_like(m); cv2.drawContours(m, cn, -1, 255, -1)
wax = np.zeros((H, W), np.uint8); wax[sy0:sy1, sx0:sx1] = m
ys, xs = np.nonzero(wax)
cx, cy = float(xs.mean()), float(ys.mean())
box = [int(xs.min()) - 8, int(ys.min()) - 8, int(xs.max()) + 9, int(ys.max()) + 9]

# ---------- 3. monograma nuevo ----------
# centro del disco interior y radio útil (medidos sobre la foto)
dcx, dcy, dr = 795.0, 517.0, 55.0
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rr = np.hypot(xx - dcx, yy - dcy)
disc = (rr < dr).astype(np.float32)
smooth = cv2.GaussianBlur(clean, (0, 0), 9)
fade = np.clip((dr - rr) / 5, 0, 1)[..., None]
sealimg = clean * (1 - fade) + smooth * fade
noise = rng.normal(0, 1.4, (H, W, 1)).astype(np.float32)
sealimg += noise * fade

S = 4
fsize = 46 * S
font = ImageFont.truetype(a.fuente, fsize)
canvas = Image.new("L", (int(dr * 2.6 * S), int(dr * 2.6 * S)), 0)
d = ImageDraw.Draw(canvas)
try:
    font.set_variation_by_axes([600])
except Exception:
    pass
text = a.iniciales
# ampersand más pequeño, como en los sellos clásicos
parts = [(text[0], 1.0), (text[1:-1], 0.62), (text[-1], 1.0)] if len(text) >= 3 else [(text, 1.0)]
fonts = [ImageFont.truetype(a.fuente, int(fsize * s)) for _, s in parts]
for f in fonts:
    try: f.set_variation_by_axes([600])
    except Exception: pass
widths = [d.textlength(t, font=f) for (t, _), f in zip(parts, fonts)]
gap = 2 * S
total = sum(widths) + gap * (len(parts) - 1)
x = canvas.width / 2 - total / 2
base = canvas.height / 2 + fsize * 0.34
for (t, s), f, w in zip(parts, fonts, widths):
    d.text((x, base), t, font=f, fill=255, anchor="ls")
    x += w + gap
mono = np.asarray(canvas.resize((canvas.width // S, canvas.height // S), Image.LANCZOS)).astype(np.float32) / 255
hgt = np.zeros((H, W), np.float32)
mh, mw = mono.shape
ox, oy = int(dcx - mw / 2), int(dcy - 4 - mh / 2)
hgt[oy:oy + mh, ox:ox + mw] = mono
hgt = cv2.GaussianBlur(hgt, (0, 0), 1.1)
gx = cv2.Sobel(hgt, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(hgt, cv2.CV_32F, 0, 1, ksize=3)
light = (-gx * 0.62 - gy * 0.78)   # luz desde arriba a la izquierda: letras en relieve
shade = 1 + np.clip(light, -1, 1)[..., None] * 0.55
top = 1 - 0.06 * hgt[..., None]     # la cara de la letra, un poco más oscura y mate
sealimg = sealimg * shade * top
# también el anillo exterior del disco se conserva tal cual (fade solo dentro de dr)

# ---------- 4. grieta y mitades ----------
p0 = np.array([box[0] + 14, cy + 6.0]); p1 = np.array([box[2] - 14, cy - 44.0])
crack = []
for i in range(25):
    t = i / 24
    p = p0 + (p1 - p0) * t
    nv = np.array([-(p1 - p0)[1], (p1 - p0)[0]]); nv /= np.linalg.norm(nv)
    crack.append(p + nv * (0 if i in (0, 24) else rng.uniform(-5, 5)))
crack = np.array(crack)
ext = np.vstack([[crack[0] - [40, 0]], crack, [crack[-1] + [40, 0]]])
upper = pmask(np.vstack([ext, [[box[2] + 40, box[1] - 40], [box[0] - 40, box[1] - 40]]]))
waxin = cv2.erode(wax, np.ones((3, 3), np.uint8), iterations=1)
A = cv2.bitwise_and(waxin, upper); B = cv2.bitwise_and(waxin, cv2.bitwise_not(upper))
x0, y0, x1, y1 = box

def piece(mask, fresh):
    rgb = sealimg[y0:y1, x0:x1].copy()
    al = cv2.GaussianBlur(mask[y0:y1, x0:x1].astype(np.float32), (0, 0), 0.7)
    if fresh:
        cm = np.zeros((y1 - y0, x1 - x0), np.uint8)
        cv2.polylines(cm, [np.int32(crack - [x0, y0])], False, 255, 5)
        e = cv2.GaussianBlur(cm.astype(np.float32) / 255, (0, 0), 1.3)[..., None] * (al[..., None] / 255)
        rgb = rgb * (1 - 0.5 * e) + np.array([70, 92, 112], np.float32) * 0.5 * e   # cera rota: más clara y mate
    return np.dstack([np.clip(rgb, 0, 255), al]).astype(np.uint8)

out = a.salida
cv2.imwrite(f"{out}/sello.png", piece(waxin, False))
cv2.imwrite(f"{out}/sello-a.png", piece(A, True))
cv2.imwrite(f"{out}/sello-b.png", piece(B, True))
cv2.imwrite(f"{out}/sello-sombra.png", (255 - cv2.GaussianBlur(wax[y0:y1, x0:x1].astype(np.float32), (0, 0), 5)).astype(np.uint8))  # oscuro bajo la cera (se mezcla en "multiply")

# ---------- 5. papel sin sello (lo que se ve por la grieta) ----------
wd = cv2.dilate(wax, np.ones((3, 3), np.uint8), iterations=2)
plate = cv2.inpaint(np.clip(clean, 0, 255).astype(np.uint8), wd, 9, cv2.INPAINT_TELEA).astype(np.float32)
plate += grain_from(clean, wd, (150, -40))
sh = cv2.GaussianBlur(cv2.erode(wax, np.ones((9, 9), np.uint8)).astype(np.float32) / 255, (0, 0), 6)[..., None]
plate *= 1 - 0.22 * sh   # el papel bajo el sello queda un poco hundido y en sombra
cv2.imwrite(f"{out}/sobre.jpg", np.clip(plate, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 88])

json.dump({"size": [W, H], "sealBox": box, "sealCenter": [round(cx, 1), round(cy, 1)],
           "crack": np.round(crack, 1).tolist(), "name": {"cx": 1070, "cy": 712, "angle": -15.5, "width": 440}},
          open(f"{out}/sobre.json", "w"))
print("listo", box, round(cx, 1), round(cy, 1))
