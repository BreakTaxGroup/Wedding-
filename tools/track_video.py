"""Seguimiento plano del sobre en el video de Gemini, borrado del nombre y exportación.

Uso: python3 track_video.py video.mp4 salida/ [ultimo_cuadro]
Genera: salida/apertura.mp4 (sin nombre), salida/poster.jpg, salida/track.json (homografías por cuadro)
"""
import sys, json, os, subprocess, tempfile
import numpy as np, cv2

SRC, OUT = sys.argv[1], sys.argv[2]
LAST = int(sys.argv[3]) if len(sys.argv) > 3 else 56
os.makedirs(OUT, exist_ok=True)
cap = cv2.VideoCapture(SRC)
fps = cap.get(cv2.CAP_PROP_FPS)
frames = []
for i in range(LAST + 1):
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
H0, W0 = frames[0].shape[:2]

def pmask(pts, dil=0):
    m = np.zeros((H0, W0), np.uint8)
    cv2.fillPoly(m, [np.int32(pts)], 255)
    if dil: m = cv2.dilate(m, np.ones((3, 3), np.uint8), iterations=dil)
    return m

# zona del cuerpo del sobre en el cuadro 0 (debajo de la solapa, sin el lacre)
body = [(200, 262), (560, 300), (612, 330), (640, 410), (760, 420), (800, 300), (1000, 150), (1085, 140),
        (1255, 505), (1250, 560), (262, 718), (215, 450)]
feat_mask = pmask(body)
cv2.circle(feat_mask, (697, 336), 100, 0, -1)
name_poly = [(726, 522), (1108, 416), (1152, 428), (1152, 482), (772, 592), (733, 588)]

sift = cv2.SIFT_create(nfeatures=4000, contrastThreshold=0.02)
g0 = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
k0, d0 = sift.detectAndCompute(g0, feat_mask)
bf = cv2.BFMatcher(cv2.NORM_L2)
Hs = [np.eye(3)]
prevH = np.eye(3)
for i in range(1, len(frames)):
    g = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
    # buscar solo cerca de donde debería estar el cuerpo
    wm = cv2.warpPerspective(cv2.dilate(feat_mask, np.ones((25, 25), np.uint8)), prevH, (W0, H0))
    k, d = sift.detectAndCompute(g, wm)
    ms = bf.knnMatch(d0, d, k=2)
    good = [m for m, n in ms if m.distance < 0.75 * n.distance]
    src = np.float32([k0[m.queryIdx].pt for m in good])
    dst = np.float32([k[m.trainIdx].pt for m in good])
    H, inl = cv2.findHomography(src, dst, cv2.RANSAC, 2.5, maxIters=5000, confidence=0.999)
    if H is None or inl.sum() < 25:
        H = prevH
    Hs.append(H); prevH = H
    print(f"cuadro {i:02d}: {len(good)} coincidencias, {int(inl.sum()) if inl is not None else 0} válidas", flush=True)

# suavizado temporal: trayectorias de 4 esquinas alrededor del nombre
corners = np.float32([[700, 380], [1180, 380], [1180, 620], [700, 620]]).reshape(-1, 1, 2)
traj = np.array([cv2.perspectiveTransform(corners, H).reshape(-1, 2) for H in Hs])  # T x 4 x 2
sm = traj.copy()
for t in range(len(traj)):
    a, b = max(0, t - 2), min(len(traj), t + 3)
    w = np.array([1, 2, 3, 2, 1], np.float32)[(a - t + 2):(b - t + 2)]
    sm[t] = (traj[a:b] * w[:, None, None]).sum(0) / w.sum()
sm[0] = traj[0]
Hs = [cv2.getPerspectiveTransform(corners.reshape(-1, 2), sm[t].astype(np.float32)) for t in range(len(traj))]

# borrar el nombre en el cuadro 0
f0 = frames[0]
gray = cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY).astype(np.float32)
npoly = pmask(name_poly)
bg = cv2.medianBlur(gray.astype(np.uint8), 31).astype(np.float32)
ink = (((bg - gray) > 9) & (npoly > 0)).astype(np.uint8) * 255
ink = cv2.dilate(ink, np.ones((3, 3), np.uint8), iterations=3)
clean0 = cv2.inpaint(f0, ink, 5, cv2.INPAINT_TELEA).astype(np.float32)
hf = f0.astype(np.float32) - cv2.GaussianBlur(f0.astype(np.float32), (0, 0), 2.0)
hf = cv2.warpAffine(hf, np.float32([[1, 0, 0], [0, 1, 85]]), (W0, H0), borderMode=cv2.BORDER_REFLECT)
km = cv2.GaussianBlur(ink.astype(np.float32) / 255, (0, 0), 1.5)[..., None]
clean0 = clean0 + hf * km * 0.9

region = pmask(name_poly, dil=6)
feather = cv2.GaussianBlur(region.astype(np.float32) / 255, (0, 0), 4)
ring = (pmask(name_poly, dil=16) > 0) & (region == 0)

tmp = tempfile.mkdtemp()
for i, (f, H) in enumerate(zip(frames, Hs)):
    wc = cv2.warpPerspective(clean0, H, (W0, H0), flags=cv2.INTER_CUBIC)
    m = cv2.warpPerspective(feather, H, (W0, H0))[..., None]
    rg = cv2.warpPerspective(ring.astype(np.uint8), H, (W0, H0)) > 0
    ff = f.astype(np.float32)
    gain = (ff[rg].mean(0) + 1) / (wc[rg].mean(0) + 1)
    out = ff * (1 - m) + wc * gain * m
    cv2.imwrite(f"{tmp}/f{i:03d}.png", np.clip(out, 0, 255).astype(np.uint8))
    if i == 0:
        cv2.imwrite(f"{OUT}/poster.jpg", np.clip(out, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 90])

dur = len(frames) / fps
subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(fps), "-i", f"{tmp}/f%03d.png", "-i", SRC,
                "-map", "0:v", "-map", "1:a", "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "19",
                "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart",
                "-af", f"afade=t=out:st={max(0, dur - 0.5):.2f}:d=0.5,volume=2.2", "-c:a", "aac", "-b:a", "128k",
                f"{OUT}/apertura.mp4"], check=True)
json.dump({"fps": fps, "size": [W0, H0], "frames": len(frames),
           "H": [np.round(H / H[2, 2], 6).tolist() for H in Hs],
           "name": {"center": [937, 505], "angle": -16.5}}, open(f"{OUT}/track.json", "w"))
print("listo", len(frames), "cuadros", round(dur, 2), "s")
