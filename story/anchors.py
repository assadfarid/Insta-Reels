"""Auto-detect speaker head positions (normalised source coords) for speech bubbles."""
import json, cv2, numpy as np
exec(open('script.py').read())
pairs = sorted({(sc, sp) for sc, sp, tx, h in LINES if sp not in ('N',) and sc.startswith('s')})

def echo_head(im):
    hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV)
    m = cv2.inRange(hsv, (78, 90, 170), (100, 255, 255))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    idx = [i for i in range(1, n) if 150 < st[i][4] < 60000]
    idx = sorted(idx, key=lambda i: -st[i][4])[:2]
    if not idx: return None
    c = np.mean([cen[i] for i in idx], axis=0)
    return float(c[0] / im.shape[1]), float(c[1] / im.shape[0])

def mia_head(im):
    hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    m = (((H < 8) | (H > 172)) & (S > 120) & (V > 60) & (V < 215)).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n < 2: return None
    i = max(range(1, n), key=lambda i: st[i][4])
    x, y, w, h, a = st[i]
    hx = x + w / 2; hy = y - h * 0.9
    return float(hx / im.shape[1]), float(max(0.02, hy / im.shape[0]))

out = {}
for sc, sp in pairs:
    im = cv2.cvtColor(cv2.imread(f'assets/img/{sc}.png'), cv2.COLOR_BGR2RGB)
    a = echo_head(im) if sp == 'ECHO' else mia_head(im) if sp == 'MIA' else None
    out[f'{sc}:{sp}'] = a
json.dump(out, open('anchors_auto.json', 'w'), indent=1)
print(len(out), sum(v is None for v in out.values()))
