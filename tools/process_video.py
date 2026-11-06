"""Procesa el video de Gemini para la invitación.

1. Sigue el sobre (plano) y borra el nombre impreso "Familia Martinez".
2. Sigue la tarjeta mientras sale del sobre y reemplaza su texto inventado por el real.
3. Exporta el clip, el póster y track.json (homografías para escribir en vivo el nombre de cada invitado).

Uso:
  python3 process_video.py VIDEO SALIDA FUENTES --names "Valeria & Andrés" --date "Sábado 12 de junio de 2027"
"""
import argparse, json, os, subprocess, tempfile
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("out"); ap.add_argument("fonts")
ap.add_argument("--last", type=int, default=94)
ap.add_argument("--names", default="Valeria & Andrés")
ap.add_argument("--top1", default="CON LA BENDICIÓN DE DIOS")
ap.add_argument("--top2", default="Y DE NUESTRAS FAMILIAS")
ap.add_argument("--para", default="Los invitamos a celebrar el comienzo de|nuestra vida juntos, entre árboles, luz|y las personas que más queremos.")
ap.add_argument("--date", default="SÁBADO 12 DE JUNIO DE 2027")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

cap = cv2.VideoCapture(a.video)
fps = cap.get(cv2.CAP_PROP_FPS)
F = []
for i in range(a.last + 1):
    ok, f = cap.read()
    if not ok: break
    F.append(f)
N = len(F); H0, W0 = F[0].shape[:2]
G = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in F]
sift = cv2.SIFT_create(nfeatures=5000, contrastThreshold=0.015)
bf = cv2.BFMatcher(cv2.NORM_L2)

def pmask(pts, dil=0, shape=(H0, W0)):
    m = np.zeros(shape, np.uint8); cv2.fillPoly(m, [np.int32(pts)], 255)
    if dil: m = cv2.dilate(m, np.ones((3, 3), np.uint8), iterations=dil)
    return m

def match(ga, ma, gb, mb, thr=2.5):
    ka, da = sift.detectAndCompute(ga, ma); kb, db = sift.detectAndCompute(gb, mb)
    if da is None or db is None or len(ka) < 8 or len(kb) < 8: return None, 0
    ms = bf.knnMatch(da, db, k=2)
    good = [m for m, n in (p for p in ms if len(p) == 2) if m.distance < 0.75 * n.distance]
    if len(good) < 8: return None, 0
    s = np.float32([ka[m.queryIdx].pt for m in good]); d = np.float32([kb[m.trainIdx].pt for m in good])
    H, inl = cv2.findHomography(s, d, cv2.RANSAC, thr, maxIters=6000, confidence=0.999)
    return (H, int(inl.sum())) if H is not None else (None, 0)

def track(ref, order, region, full_dil=31):
    """Homografías ref->i. Intenta directo; si no alcanza, encadena desde el cuadro vecino."""
    Hs = {ref: np.eye(3)}; conf = {ref: 999}
    big = np.ones((H0, W0), np.uint8) * 255
    prev = ref
    for i in order:
        wm = cv2.warpPerspective(cv2.dilate(region, np.ones((full_dil, full_dil), np.uint8)), Hs[prev], (W0, H0))
        H, n = match(G[ref], region, G[i], wm if wm.sum() > 0 else big)
        if n < 40:
            pm = cv2.warpPerspective(region, Hs[prev], (W0, H0))
            Hc, nc = match(G[prev], pm, G[i], cv2.dilate(pm, np.ones((full_dil, full_dil), np.uint8)))
            if Hc is not None and nc > n:
                H, n = Hc @ Hs[prev], nc
        if H is None: H, n = Hs[prev], 0
        Hs[i] = H; conf[i] = n; prev = i
    return Hs, conf

def smooth(Hs, idx, box):
    c = np.float32(box).reshape(-1, 1, 2)
    tr = np.array([cv2.perspectiveTransform(c, Hs[i]).reshape(-1, 2) for i in idx])
    out = {}
    w0 = np.array([1, 2, 3, 2, 1], np.float32)
    for k, i in enumerate(idx):
        lo, hi = max(0, k - 2), min(len(idx), k + 3)
        w = w0[(lo - k + 2):(hi - k + 2)]
        p = (tr[lo:hi] * w[:, None, None]).sum(0) / w.sum()
        out[i] = cv2.getPerspectiveTransform(c.reshape(-1, 2), p.astype(np.float32))
    return out

def gainmatch(frame, warped, mask):
    m = mask > 0.5
    if m.sum() < 50: return np.ones(3, np.float32)
    return (np.median(frame[m], 0) + 1) / (np.median(warped[m], 0) + 1)

def relight(frame, warped_orig, sigma=14):
    """Mapa de luz local: cuadro / referencia deformada (ambos con el mismo texto original)."""
    a_ = cv2.GaussianBlur(frame, (0, 0), sigma) + 2
    b_ = cv2.GaussianBlur(warped_orig, (0, 0), sigma) + 2
    return np.clip(a_ / b_, 0.6, 1.6)

def visible(frame, warped_orig, mask, thr=20):
    g1 = cv2.GaussianBlur(cv2.cvtColor(np.clip(frame, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 3)
    gw = cv2.cvtColor(np.clip(warped_orig, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    gain = gainmatch(frame, warped_orig, mask)
    g2 = cv2.GaussianBlur(gw * float(gain.mean()), (0, 0), 3)
    v = (np.abs(g1 - g2) < thr).astype(np.uint8) * 255
    v = cv2.morphologyEx(v, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    v = cv2.morphologyEx(v, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    return cv2.GaussianBlur(v.astype(np.float32) / 255, (0, 0), 2)

# ---------------- 1. sobre ----------------
body = [(200, 262), (560, 300), (612, 330), (640, 410), (760, 420), (800, 300), (1000, 150), (1085, 140),
        (1255, 505), (1250, 560), (262, 718), (215, 450)]
env_region = pmask(body); cv2.circle(env_region, (697, 336), 100, 0, -1)
name_poly = [(726, 522), (1108, 416), (1152, 428), (1152, 482), (772, 592), (733, 588)]
envH, envC = track(0, range(1, N), env_region)
name_box = [[700, 380], [1180, 380], [1180, 620], [700, 620]]
envH = smooth(envH, list(range(N)), name_box)
print("sobre: confianza", [envC[i] for i in range(0, N, 6)], flush=True)

f0 = F[0].astype(np.float32)
g0 = G[0].astype(np.float32)
npoly = pmask(name_poly)
bg = cv2.medianBlur(G[0], 31).astype(np.float32)
ink = (((bg - g0) > 9) & (npoly > 0)).astype(np.uint8) * 255
ink = cv2.dilate(ink, np.ones((3, 3), np.uint8), iterations=3)
env_clean = cv2.inpaint(F[0], ink, 5, cv2.INPAINT_TELEA).astype(np.float32)
hf = f0 - cv2.GaussianBlur(f0, (0, 0), 2.0)
hf = cv2.warpAffine(hf, np.float32([[1, 0, 0], [0, 1, 85]]), (W0, H0), borderMode=cv2.BORDER_REFLECT)
env_clean += hf * cv2.GaussianBlur(ink.astype(np.float32) / 255, (0, 0), 1.5)[..., None] * 0.9
env_reg = cv2.GaussianBlur(pmask(name_poly, dil=6).astype(np.float32) / 255, (0, 0), 4)

# ---------------- 2. tarjeta ----------------
REF = N - 1
card_rough = pmask([(300, 0), (995, 0), (1000, 719), (285, 719)])
cardH, cardC = track(REF, range(REF - 1, 40, -1), card_rough)
print("tarjeta: confianza", [cardC.get(i) for i in range(REF, 40, -6)], flush=True)
corners86 = np.float32([[398, 22], [868, 2], [922, 600], [407, 625]]).reshape(-1, 1, 2)
card_ref_corners = cv2.perspectiveTransform(corners86, np.linalg.inv(cardH[86])).reshape(-1, 2)
# cuadros tempranos (tarjeta dentro del sobre): alineación densa cuadro a cuadro (ECC) hacia atrás
ANCHOR = 70
top_ref = np.float32([card_ref_corners[0], card_ref_corners[1],
                      card_ref_corners[1] + (card_ref_corners[2] - card_ref_corners[1]) * 0.6,
                      card_ref_corners[0] + (card_ref_corners[3] - card_ref_corners[0]) * 0.6])
top_mask_ref = np.zeros((H0, W0), np.uint8)
_tl = cv2.perspectiveTransform(top_ref.reshape(-1, 1, 2), np.eye(3)).reshape(-1, 2)
def ecc_step(Ht, gi, gt, mask):
    W = np.eye(3, dtype=np.float32)
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 120, 1e-6)
    for sc in (0.5, 1.0):
        t = cv2.resize(gt, None, fx=sc, fy=sc).astype(np.float32); im = cv2.resize(gi, None, fx=sc, fy=sc).astype(np.float32)
        mk = cv2.resize(mask, None, fx=sc, fy=sc, interpolation=cv2.INTER_NEAREST)
        S = np.diag([sc, sc, 1]).astype(np.float32); Ws = S @ W @ np.linalg.inv(S)
        try:
            _, Ws = cv2.findTransformECC(t, im, Ws.astype(np.float32), cv2.MOTION_HOMOGRAPHY, crit, mk, 5)
            W = np.linalg.inv(S) @ Ws @ S
        except cv2.error:
            pass
    return W
for i in range(ANCHOR - 1, 47, -1):
    tq = cv2.perspectiveTransform(top_ref.reshape(-1, 1, 2), cardH[i + 1]).reshape(-1, 2)
    mk = np.zeros((H0, W0), np.uint8); cv2.fillPoly(mk, [np.int32(tq)], 255)
    mk = cv2.erode(mk, np.ones((7, 7), np.uint8))
    if mk.sum() < 255 * 400: cardH[i] = cardH[i + 1]; cardC[i] = 0; continue
    W = ecc_step(None, G[i], G[i + 1], mk)
    cardH[i] = W @ cardH[i + 1]; cardC[i] = 50
first_card = 48
for i in list(cardH):
    if i < first_card: del cardH[i]
card_idx = [i for i in range(first_card, N)]
cardH = smooth(cardH, card_idx, card_ref_corners)

ref = F[REF].astype(np.float32); gref = G[REF].astype(np.float32)
boxes = {"top": (468, 98, 832, 156), "names": (462, 288, 838, 368), "para": (438, 404, 852, 480), "count": (502, 490, 792, 548)}
tm = np.zeros((H0, W0), np.uint8); ink_c = np.zeros((H0, W0), np.uint8)
bgr = cv2.medianBlur(G[REF], 25).astype(np.float32)
for (x0, y0, x1, y1) in boxes.values():
    tm[y0:y1, x0:x1] = 255
    sub = ((bgr[y0:y1, x0:x1] - gref[y0:y1, x0:x1]) > 7).astype(np.uint8) * 255
    ink_c[y0:y1, x0:x1] = sub
_nb = ((bgr - gref) > 14) & (pmask([(450, 170), (870, 170), (870, 255), (450, 255)]) > 0)
_sel = ref[_nb]
_lum = _sel.mean(1)
ink_col = np.median(_sel[_lum <= np.percentile(_lum, 25)], 0)
ink_c = cv2.dilate(ink_c, np.ones((3, 3), np.uint8), iterations=4)
card_clean = cv2.inpaint(F[REF], ink_c, 6, cv2.INPAINT_TELEA)

# texto real
SS = 3
img = Image.fromarray(cv2.cvtColor(card_clean, cv2.COLOR_BGR2RGB)).resize((W0 * SS, H0 * SS), Image.LANCZOS)
lay = Image.new("L", img.size, 0); d = ImageDraw.Draw(lay)
def font(name, size): return ImageFont.truetype(os.path.join(a.fonts, name), int(size * SS))
def spaced(text, f, cx, base, track_px):
    w = sum(d.textlength(ch, font=f) for ch in text) + track_px * SS * (len(text) - 1)
    x = cx * SS - w / 2
    for ch in text:
        d.text((x, base * SS), ch, font=f, fill=255, anchor="ls"); x += d.textlength(ch, font=f) + track_px * SS
CX = 648
spaced(a.top1, font("Cinzel.ttf", 15.5), CX, 124, 1.6)
spaced(a.top2, font("Cinzel.ttf", 15.5), CX, 147, 1.6)
fn = font("Parisienne.ttf", 52)
d.text((CX * SS, 347 * SS), a.names, font=fn, fill=255, anchor="ms", stroke_width=1, stroke_fill=255)
for k, line in enumerate(a.para.split("|")):
    d.text((CX * SS, (426 + k * 19) * SS), line, font=font("EBGaramond.ttf", 14.5), fill=230, anchor="ms")
spaced(a.date, font("Cinzel.ttf", 17), CX, 525, 1.2)
lay = lay.filter(ImageFilter.GaussianBlur(0.6 * SS)).resize((W0, H0), Image.LANCZOS)
alpha = np.clip(np.asarray(lay).astype(np.float32)[..., None] / 255 * 1.0, 0, 1)
card_baked = card_clean.astype(np.float32) * (1 - alpha) + ink_col[None, None, :] * alpha
card_reg = cv2.GaussianBlur(cv2.dilate(tm, np.ones((5, 5), np.uint8), iterations=4).astype(np.float32) / 255, (0, 0), 7)

# ---------------- 3. componer cuadros ----------------
tmp = tempfile.mkdtemp()
frames_meta = []
name_zone = pmask(name_poly, dil=4)
for i in range(N):
    fr = F[i].astype(np.float32)
    out = fr.copy()
    # sobre: borrar nombre donde el papel está visible
    He = envH[i]
    if envC.get(i, 999) >= 12:
        wc = cv2.warpPerspective(env_clean, He, (W0, H0), flags=cv2.INTER_CUBIC)
        wo = cv2.warpPerspective(f0, He, (W0, H0), flags=cv2.INTER_CUBIC)
        m = cv2.warpPerspective(env_reg, He, (W0, H0))
        vis = visible(fr, wo, m) if i > 40 else np.ones((H0, W0), np.float32)
        mm = (m * vis)[..., None]
        out = out * (1 - mm) + wc * relight(fr, wo) * mm
        nz = cv2.warpPerspective(name_zone, He, (W0, H0)) > 0
        occl = float(1 - vis[nz].mean()) if nz.sum() > 0 else 0.0
        inside = float(nz.sum()) / max(1, int((name_zone > 0).sum()))
    else:
        occl, inside = 1.0, 0.0
    # tarjeta: texto real
    clip = None
    if i in cardH and i >= first_card:
        Hc = cardH[i]
        wb = cv2.warpPerspective(card_baked, Hc, (W0, H0), flags=cv2.INTER_CUBIC)
        wo = cv2.warpPerspective(ref, Hc, (W0, H0), flags=cv2.INTER_CUBIC)
        m = cv2.warpPerspective(card_reg, Hc, (W0, H0))
        vis = visible(fr, wo, m, thr=24) if i < REF else np.ones((H0, W0), np.float32)
        mm = (m * vis)[..., None]
        out = out * (1 - mm) + wb * relight(fr, wo) * mm
        if i >= 70:  # la tarjeta ya salió y queda delante del sobre
            clip = np.round(cv2.perspectiveTransform(card_ref_corners.reshape(-1, 1, 2), Hc).reshape(-1, 2), 1).tolist()
    # opacidad del nombre en vivo
    alpha_name = 1.0 if envC.get(i, 999) >= 12 and inside > 0.2 else 0.0
    if i > 40 and i < 70 and occl > 0.6: alpha_name = 0.0
    frames_meta.append({"H": np.round(He / He[2, 2], 6).tolist(), "a": alpha_name, "clip": clip})
    cv2.imwrite(f"{tmp}/f{i:03d}.png", np.clip(out, 0, 255).astype(np.uint8))
    if i == 0:
        cv2.imwrite(os.path.join(a.out, "poster.jpg"), np.clip(out, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 90])

dur = N / fps
subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(fps), "-i", f"{tmp}/f%03d.png", "-i", a.video,
                "-map", "0:v", "-map", "1:a", "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart",
                "-af", f"volume=2.2,afade=t=out:st={max(0, dur - 0.6):.2f}:d=0.6", "-c:a", "aac", "-b:a", "128k",
                os.path.join(a.out, "apertura.mp4")], check=True)
json.dump({"fps": fps, "size": [W0, H0], "frames": frames_meta, "name": {"center": [938, 480], "angle": -16}},
          open(os.path.join(a.out, "track.json"), "w"))
print("listo:", N, "cuadros,", round(dur, 2), "s; primera tarjeta", first_card)
