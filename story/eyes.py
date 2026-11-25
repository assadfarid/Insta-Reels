"""Detect Mia's eyes inside her (hand-marked) head box for blinking. Writes eyes.json."""
import json, cv2, numpy as np
F = json.load(open('faces2.json'))
SKIP = {'s07', 's09', 's18', 's21', 's25', 's46', 's54', 's13', 's33', 's34', 's37', 's38', 's16', 's27', 's28'}
out = {}
for sc, d in F.items():
    if 'MIA' not in d or sc in SKIP:
        continue
    im = cv2.cvtColor(cv2.imread(f'assets/img/{sc}.png'), cv2.COLOR_BGR2RGB)
    h, w = im.shape[:2]
    x0, y0, x1, y1 = d['MIA']
    X0, X1 = int(x0 * w), int(x1 * w)
    Y0, Y1 = int((y0 + (y1 - y0) * 0.30) * h), int((y0 + (y1 - y0) * 0.75) * h)
    crop = im[Y0:Y1, X0:X1]
    if crop.size == 0:
        continue
    hsv = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV)
    dark = ((hsv[..., 2] < 75)).astype(np.uint8)
    dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(dark)
    A = crop.shape[0] * crop.shape[1]
    blobs = []
    for i in range(1, n):
        x, y, bw_, bh_, a = st[i]
        if not (0.002 * A < a < 0.05 * A):
            continue
        asp = bh_ / max(1, bw_)
        if not (0.6 < asp < 2.4):
            continue
        fill = a / (bw_ * bh_)
        if fill < 0.45:
            continue
        blobs.append((x + X0, y + Y0, bw_, bh_, a))
    best = None
    for i in range(len(blobs)):
        for j in range(i + 1, len(blobs)):
            a, b = blobs[i], blobs[j]
            if abs((a[1] + a[3] / 2) - (b[1] + b[3] / 2)) > 0.35 * max(a[3], b[3]):
                continue
            ratio = max(a[4], b[4]) / min(a[4], b[4])
            if ratio > 2.5:
                continue
            sep = abs((a[0] + a[2] / 2) - (b[0] + b[2] / 2))
            if not (1.2 * max(a[2], b[2]) < sep < 0.6 * (X1 - X0)):
                continue
            score = ratio + abs(a[3] - b[3]) / max(a[3], b[3])
            if best is None or score < best[0]:
                best = (score, [a, b])
    eyes = best[1] if best else None
    if eyes:
        out[sc] = [[(e[0] + e[2] / 2) / w, (e[1] + e[3] / 2) / h, e[2] / 2 / w, e[3] / 2 / h] for e in eyes]
json.dump(out, open('eyes.json', 'w'), indent=1)
print(sorted(out))
# debug sheet: crops around Mia head with eye ellipses
from PIL import Image, ImageDraw
tiles = []
for sc, es in sorted(out.items()):
    im = Image.open(f'assets/img/{sc}.png'); w, h = im.size
    x0, y0, x1, y1 = F[sc]['MIA']
    d = ImageDraw.Draw(im)
    for cx, cy, rx, ry in es:
        d.ellipse([(cx - rx) * w, (cy - ry) * h, (cx + rx) * w, (cy + ry) * h], outline=(0, 255, 0), width=4)
    c = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))).resize((300, 300))
    ImageDraw.Draw(c).text((5, 5), sc, fill=(255, 255, 0))
    tiles.append(c)
sheet = Image.new('RGB', (6 * 300, ((len(tiles) + 5) // 6) * 300))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % 6) * 300, (i // 6) * 300))
sheet.save('test/eyes.jpg', quality=85)
