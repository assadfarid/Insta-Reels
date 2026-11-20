"""Precise face boxes (normalised source coords, x0,y0,x1,y1) per dialogue scene and character."""
import json, cv2, numpy as np
faces = json.load(open('faces.json'))
out = {}

def skin_box(im, ax, ay):
    h, w = im.shape[:2]
    hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    skin = (((H <= 22) | (H >= 172)) & (S > 35) & (S < 185) & (V > 85)).astype(np.uint8)
    R = int(0.17 * w)
    x0, y0 = max(0, int(ax * w) - R), max(0, int(ay * h) - R)
    x1, y1 = min(w, int(ax * w) + R), min(h, int(ay * h) + R)
    sub = cv2.morphologyEx(skin[y0:y1, x0:x1], cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(sub)
    best = None
    for i in range(1, n):
        if st[i][4] < 0.0006 * w * h:
            continue
        cx, cy = cen[i][0] + x0, cen[i][1] + y0
        d = np.hypot(cx - ax * w, cy - ay * h)
        if best is None or d < best[0]:
            best = (d, st[i])
    if best is None or best[0] > 0.12 * w:
        return None
    x, y, bw, bh, a = best[1]
    x += x0; y += y0
    # add hair / head margin
    X0, X1 = x - 0.35 * bw, x + bw * 1.35
    Y0, Y1 = y - 0.75 * bh, y + bh * 1.05
    return [X0 / w, Y0 / h, X1 / w, Y1 / h]

def echo_box(im, ax, ay):
    h, w = im.shape[:2]
    hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV)
    m = cv2.inRange(hsv, (78, 90, 170), (100, 255, 255))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    idx = [i for i in range(1, n) if 150 < st[i][4] < 60000 and np.hypot(cen[i][0] - ax * w, cen[i][1] - ay * h) < 0.2 * w]
    idx = sorted(idx, key=lambda i: -st[i][4])[:2]
    if len(idx) == 2:
        span = abs(cen[idx[0]][0] - cen[idx[1]][0]) + max(st[idx[0]][2], st[idx[1]][2])
        cx, cy = (cen[idx[0]][0] + cen[idx[1]][0]) / 2, (cen[idx[0]][1] + cen[idx[1]][1]) / 2
    else:
        span = 0.09 * w; cx, cy = ax * w, ay * h
    return [(cx - 1.45 * span) / w, (cy - 1.55 * span) / h, (cx + 1.45 * span) / w, (cy + 1.15 * span) / h]

for sc, pts in faces.items():
    im = cv2.cvtColor(cv2.imread(f'assets/img/{sc}.png'), cv2.COLOR_BGR2RGB)
    out[sc] = {}
    for who, (ax, ay) in pts.items():
        if who == 'ECHO':
            b = echo_box(im, ax, ay)
        else:
            b = skin_box(im, ax, ay)
            if b is None:
                b = [ax - 0.08, ay - 0.13, ax + 0.08, ay + 0.11]
        out[sc][who] = [round(v, 4) for v in b]
json.dump(out, open('faces2.json', 'w'), indent=1)

# debug sheets
from PIL import Image, ImageDraw
scs = sorted(out)
for part in range(2):
    sub = scs[part * 20:(part + 1) * 20]
    W, Hh = 480, 271
    sheet = Image.new('RGB', (5 * W, ((len(sub) + 4) // 5) * Hh))
    for i, sc in enumerate(sub):
        im = Image.open(f'assets/img/{sc}.png').resize((W, Hh)); d = ImageDraw.Draw(im)
        for who, (x0, y0, x1, y1) in out[sc].items():
            col = {'MIA': (255, 0, 255), 'ECHO': (0, 255, 0)}.get(who, (255, 255, 0))
            d.rectangle([x0 * W, y0 * Hh, x1 * W, y1 * Hh], outline=col, width=3)
        d.text((5, 5), sc, fill=(255, 255, 255))
        sheet.paste(im, ((i % 5) * W, (i // 5) * Hh))
    sheet.save(f'test/fbox{part}.jpg', quality=80)
print(len(out))
