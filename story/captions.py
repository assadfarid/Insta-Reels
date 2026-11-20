"""Burned-in captions: narrator subtitles (bottom) and character speech bubbles.

Inter Bold with tight tracking. Bubbles anchor to the speaker's head (anchors.json,
normalised source-image coords) and follow the camera move via the shot's affine M.
"""
import json, re, math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

INTER = 'assets/fonts/inter-latin-700-normal.woff'
KIDS = 'assets/fonts/fredoka-latin-600-normal.woff'
exec(open('script.py').read())  # LINES
ANCH = json.load(open('anchors.json'))
FACES = json.load(open('faces.json'))
FACES2 = json.load(open('faces2.json'))
TL_HUDS = json.load(open('timeline.json'))['huds']
# close-up shots: faces are much bigger on screen
FACE_SCALE = {'s03': 1.6, 's04': 1.8, 's05': 1.8, 's12': 1.8, 's32': 1.8, 's46': 1.8, 's47': 2.4,
              's54': 1.8, 's44': 1.5, 's25': 1.4, 's07': 1.2, 's09': 1.2}


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def chunk(text, maxc):
    """Split into display chunks at sentence breaks, each <= maxc chars when possible."""
    parts = re.split(r'(?<=[.!?…])\s+', text.strip())
    out, cur = [], ''
    for p in parts:
        if not cur:
            cur = p
        elif len(cur) + 1 + len(p) <= maxc:
            cur += ' ' + p
        else:
            out.append(cur); cur = p
    if cur:
        out.append(cur)
    res = []
    for c in out:  # very long single sentence: split at commas/words
        while len(c) > maxc * 1.25:
            cut = c.rfind(', ', 0, maxc)
            cut = cut + 1 if cut > maxc * 0.4 else c.rfind(' ', 0, maxc)
            res.append(c[:cut].strip()); c = c[cut:].strip()
        res.append(c)
    return res


def wrap(text, font, maxw, track):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if tw(t, font, track) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines


def tw(text, font, track):
    return font.getlength(text) + track * max(0, len(text) - 1)


def draw_tracked(d, xy, text, font, fill, track):
    x, y = xy
    for i, ch in enumerate(text):
        d.text((x + font.getlength(text[:i]) + track * i, y), ch, font=font, fill=fill)


class Captions:
    def __init__(self, tl, W, H):
        self.W, self.H = W, H
        self.S = S = W / 1920
        self.f_sub = ImageFont.truetype(KIDS, int(48 * S))
        self.f_bub = ImageFont.truetype(KIDS, int(34 * S))
        self.track_sub = -0.8 * S   # tight letter spacing
        self.track_bub = -0.6 * S
        self.items = []
        WT = json.load(open('word_times.json'))
        for ln in tl['lines']:
            scene = LINES[ln['idx']][0]
            sp = ln['speaker']
            if sp == 'N' and str(ln['idx']) in WT:
                words = WT[str(ln['idx'])]
                k = 0
                for c in chunk(ln['text'], 84):
                    n = len(c.split())
                    ws = words[k:k + n]; k += n
                    self.items.append({'sp': 'N', 'who': sp, 'scene': scene, 'text': c, 'words': ws,
                                       'a': ws[0][1] - 0.12, 'b': ws[-1][2] + 0.35})
                continue
            maxc = 84 if sp == 'N' else 54
            chunks = chunk(ln['text'], maxc)
            total = ln['dur'] + 0.35
            L = sum(len(c) for c in chunks)
            t = ln['start'] - 0.05
            for c in chunks:
                d = total * len(c) / L
                self.items.append({'sp': sp, 'scene': scene, 'text': c, 'a': t, 'b': t + d})
                t += d
        # a bubble closes as soon as the next one opens (no overlapping bubbles)
        bub = sorted([i for i in self.items if i['sp'] != 'N'], key=lambda i: i['a'])
        for a_, b_ in zip(bub, bub[1:]):
            if b_['a'] - 0.2 < a_['b']:
                a_['b'] = max(a_['a'] + 0.4, b_['a'] - 0.2)
        self._cache = {}

    # ---------------- rendering of individual elements (cached RGBA) ----------
    NAME = {'MIA': ('Mia:', (255, 150, 170)), 'ECHO': ('Echo:', (110, 225, 245)),
            'ELENA': ('Dr. Elena:', (160, 195, 255)), 'OP': ('Radio:', (255, 205, 110)),
            'TECH': ('Technician:', (240, 190, 130))}

    def _subtitle(self, text, who='N'):
        key = ('sub3', text, who)
        if key in self._cache:
            return self._cache[key]
        S, f, tr = self.S, self.f_sub, self.track_sub
        prefix = self.NAME[who][0] + ' ' if who in self.NAME else ''
        npre = len(prefix.split())
        text = prefix + text
        lines = wrap(text, f, 1500 * S, tr)
        lh = int(58 * S)
        w = int(max(tw(l, f, tr) for l in lines) + 80 * S)
        h = int(lh * len(lines) + 40 * S)
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ds = ImageDraw.Draw(sh)
        spans = []
        for i, l in enumerate(lines):
            x = (w - tw(l, f, tr)) / 2
            y = 18 * S + i * lh
            draw_tracked(ds, (x, y + 2 * S), l, f, (0, 0, 0, 255), tr)
            pos = 0
            for wd in l.split(' '):
                j = l.index(wd, pos)
                x0 = x + f.getlength(l[:j]) + tr * j
                x1 = x + f.getlength(l[:j + len(wd)]) + tr * (j + len(wd))
                spans.append((int(y - 4 * S), int(y + lh), x0, x1))
                pos = j + len(wd)
        sh = sh.filter(ImageFilter.GaussianBlur(5 * S))
        base = Image.alpha_composite(Image.new('RGBA', (w, h), (0, 0, 0, 0)), sh)
        base = Image.alpha_composite(base, sh)
        white, green = base.copy(), base.copy()
        dw, dg = ImageDraw.Draw(white), ImageDraw.Draw(green)
        for i, l in enumerate(lines):
            x = (w - tw(l, f, tr)) / 2
            y = 18 * S + i * lh
            draw_tracked(dw, (x, y), l, f, (255, 252, 245, 255), tr)
            draw_tracked(dg, (x, y), l, f, (255, 210, 60, 255), tr)
        if npre:  # speaker name in its own colour, same in both layers
            l0 = lines[0]
            x = (w - tw(l0, f, tr)) / 2
            col = self.NAME[who][1] + (255,)
            draw_tracked(dw, (x, 18 * S), prefix.strip(), f, col, tr)
            draw_tracked(dg, (x, 18 * S), prefix.strip(), f, col, tr)
        spans = spans[npre:]
        res = (np.asarray(white).astype(np.float32), np.asarray(green).astype(np.float32), spans)
        self._cache[key] = res
        return res

    def _subtitle_old(self, text):
        key = ('sub', text)
        if key in self._cache:
            return self._cache[key]
        S, f, tr = self.S, self.f_sub, self.track_sub
        lines = wrap(text, f, 1500 * S, tr)
        lh = int(56 * S)
        w = int(max(tw(l, f, tr) for l in lines) + 80 * S)
        h = int(lh * len(lines) + 40 * S)
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ds = ImageDraw.Draw(sh)
        for i, l in enumerate(lines):
            x = (w - tw(l, f, tr)) / 2
            y = 18 * S + i * lh
            draw_tracked(ds, (x, y + 2 * S), l, f, (0, 0, 0, 255), tr)
        sh = sh.filter(ImageFilter.GaussianBlur(5 * S))
        sh = Image.eval(sh, lambda v: v)  # keep
        im = Image.alpha_composite(im, sh)
        im = Image.alpha_composite(im, sh)  # stronger soft shadow
        d = ImageDraw.Draw(im)
        for i, l in enumerate(lines):
            x = (w - tw(l, f, tr)) / 2
            y = 18 * S + i * lh
            draw_tracked(d, (x, y), l, f, (255, 252, 245, 255), tr)
        arr = np.asarray(im).astype(np.float32)
        self._cache[key] = arr
        return arr

    STYLE = {
        'MIA': dict(fill=(255, 250, 240), edge=(225, 120, 95), text=(45, 32, 28)),
        'ECHO': dict(fill=(240, 252, 255), edge=(70, 205, 230), text=(18, 40, 52)),
        'ELENA': dict(fill=(225, 240, 255), edge=(120, 175, 255), text=(20, 35, 70)),
        'OP': dict(fill=(30, 36, 44), edge=(150, 230, 245), text=(215, 245, 250)),
        'TECH': dict(fill=(255, 248, 235), edge=(185, 145, 95), text=(50, 38, 25)),
    }

    def _bubble(self, text, sp):
        key = ('bub', text, sp)
        if key in self._cache:
            return self._cache[key]
        S, f, tr = self.S, self.f_bub, self.track_bub
        st = self.STYLE[sp]
        lines = wrap(text, f, 560 * S, tr)
        lh = int(48 * S)
        padx, pady = int(30 * S), int(20 * S)
        bw = int(max(tw(l, f, tr) for l in lines) + 2 * padx)
        bh = int(lh * len(lines) + 2 * pady - 4 * S)
        m = int(16 * S)  # margin for shadow
        im = Image.new('RGBA', (bw + 2 * m, bh + 2 * m), (0, 0, 0, 0))
        shadow = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle([m, m + 4 * S, m + bw, m + bh + 4 * S], radius=int(26 * S),
                                                 fill=(0, 0, 0, 90))
        im = Image.alpha_composite(im, shadow.filter(ImageFilter.GaussianBlur(7 * S)))
        d = ImageDraw.Draw(im)
        rad = int(10 * S) if sp in ('OP', 'ELENA') else int(26 * S)
        d.rounded_rectangle([m, m, m + bw, m + bh], radius=rad, fill=st['fill'] + (246,),
                            outline=st['edge'] + (255,), width=max(2, int(3 * S)))
        for i, l in enumerate(lines):
            draw_tracked(d, (m + padx, m + pady + i * lh - 3 * S), l, f, st['text'] + (255,), tr)
        arr = np.asarray(im).astype(np.float32)
        self._cache[key] = (arr, m, bw, bh)
        if len(self._cache) > 300:
            self._cache.clear()
        return self._cache[key]

    # ---------------- compositing ----------------
    @staticmethod
    def _blend(out, lay, x, y, alpha):
        H, W = out.shape[:2]
        h, w = lay.shape[:2]
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        sub = lay[y0 - y:y1 - y, x0 - x:x1 - x]
        a = sub[..., 3:4] / 255.0 * alpha
        out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - a) + sub[..., :3] * a

    def _tail(self, out, bx, by, bw, bh, hx, hy, sp, alpha, below):
        """Draw a small triangular tail from the bubble edge toward (hx, hy)."""
        st = self.STYLE[sp]
        S = self.S
        cx = min(max(hx, bx + 40 * S), bx + bw - 40 * S)
        ey = by + bh if not below else by
        dist = math.hypot(hx - cx, hy - ey)
        L = min(48 * S, max(18 * S, dist * 0.6))
        ux, uy = (hx - cx) / (dist + 1e-6), (hy - ey) / (dist + 1e-6)
        tip = (cx + ux * L, ey + uy * L)
        half = 16 * S
        pts = [(cx - half, ey), (cx + half, ey), tip]
        x0 = int(min(p[0] for p in pts) - 6); y0 = int(min(p[1] for p in pts) - 6)
        x1 = int(max(p[0] for p in pts) + 6); y1 = int(max(p[1] for p in pts) + 6)
        im = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        rel = [(p[0] - x0, p[1] - y0) for p in pts]
        d.polygon(rel, fill=st['fill'] + (246,))
        d.line([rel[0], rel[2], rel[1]], fill=st['edge'] + (255,), width=max(2, int(3 * S)))
        # cover the bubble border where the tail joins
        jy = (ey - y0) + (-2 * S if not below else 2 * S)
        d.line([(rel[0][0] + 3 * S, jy), (rel[1][0] - 3 * S, jy)], fill=st['fill'] + (255,), width=max(3, int(5 * S)))
        self._blend(out, np.asarray(im).astype(np.float32), x0, y0, alpha)

    def draw(self, out, t, shot_M, hud_active, get_M=None):
        """shot_M: dict scene -> (M, src_w, src_h) for currently visible image shots."""
        W, H, S = self.W, self.H, self.S
        # only one narrator subtitle at a time: the most recently started one
        cur_n = None
        for it in self.items:
            if it['sp'] == 'N' and it['a'] - 0.15 <= t < it['b'] + 0.2:
                if cur_n is None or it['a'] > cur_n['a']:
                    cur_n = it
        for it in self.items:
            if it['sp'] == 'N' and it is not cur_n:
                continue
            if not (it['a'] - 0.15 <= t < it['b'] + 0.2):
                continue
            fade = min(ease((t - it['a'] + 0.15) / 0.18), 1 - ease((t - it['b']) / 0.2))
            if fade <= 0:
                continue
            if it['sp'] == 'N':
                white, green, spans = self._subtitle(it['text'], it.get('who', 'N'))
                lay = white.copy()
                for (y0, y1, x0, x1), (_, ta, tb) in zip(spans, it.get('words', [])):
                    if t <= ta:
                        break
                    frac = 1.0 if t >= tb else (t - ta) / max(0.05, tb - ta)
                    xa, xb = int(x0 - 2), int(x0 + (x1 - x0) * frac + (2 if frac >= 1 else 0))
                    lay[max(0, y0):y1, max(0, xa):xb] = green[max(0, y0):y1, max(0, xa):xb]
                h, w = lay.shape[:2]
                x = int((W - w) / 2)
                y = int(H - h - 46 * S + (1 - fade) * 8 * S)
                self._blend(out, lay, x, y, fade)
                continue
            if it['scene'] not in shot_M:
                continue
            M, sw, sh = shot_M[it['scene']]
            plc = self._place(it, get_M, M, sw, sh)
            if plc is None:
                continue
            bw, bh = plc['bw'], plc['bh']
            # --- springy pop-in, gentle float, soft shrink-out -------------
            p = (t - (it['a'] - 0.15)) / 0.42
            if p < 1:
                q = min(max(p, 0.0), 1.0) - 1
                sc = 0.3 + 0.7 * (1 + 2.4 * q ** 3 + 1.4 * q ** 2)   # easeOutBack
            else:
                sc = 1.0
            if t > it['b']:
                sc *= 1 - 0.18 * ease((t - it['b']) / 0.2)
            alpha = min(1.0, max(0.0, (t - (it['a'] - 0.15)) / 0.12)) * (1 - ease((t - it['b']) / 0.2))
            if alpha <= 0:
                continue
            # follow the camera: placement is stored in source-image coordinates
            bx, by = M @ np.array([plc['sx'], plc['sy'], 1.0])
            tipx_s, tipy_s = M @ np.array([plc['tx'], plc['ty'], 1.0])
            seed = (sum(map(ord, it['text'])) % 97) / 15.0
            by += math.sin((t - it['a']) * 2.1 + seed) * 2.5 * S
            bx += math.sin((t - it['a']) * 1.3 + seed * 2) * 1.2 * S
            cx = plc['cx']
            tdx, tdy = tipx_s - (bx + cx), tipy_s - (by + bh)
            _L = math.hypot(tdx, tdy) + 1e-6
            if _L < 52 * S:                       # always a clearly visible tail
                tdx, tdy = tdx * 52 * S / _L, tdy * 52 * S / _L
            arr, (px, py), tip = self._comic(it['text'], it['sp'], cx, tdx, tdy, plc['mirror'])
            if abs(sc - 1) > 0.01:
                img = cv2.resize(arr, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR)
            else:
                img = arr
            tipx = bx + tip[0] - px
            tipy = by + tip[1] - py
            self._blend(out, img, int(tipx - tip[0] * sc), int(tipy - tip[1] * sc), alpha)


# ---------------------------------------------------------------------------
#  Comic-book speech bubbles: white, thick black outline, hard offset shadow,
#  hand-drawn wobble, curved tail. Oval + halftone for hologram / radio voices.
# ---------------------------------------------------------------------------
INK = (22, 20, 20)


def _comic_size(self, text, sp):
    key = ('csz', text, sp)
    if key not in self._cache:
        S, f, tr = self.S, self.f_bub, self.track_bub
        lines = wrap(text, f, 430 * S, tr)
        lh = int(44 * S)
        tw_ = max(tw(l, f, tr) for l in lines)
        bw = int(max(tw_ + 64 * S, 170 * S))
        bh = int(lh * len(lines) + 40 * S)
        self._cache[key] = (bw, bh, lines, lh)
    return self._cache[key][:2]


MOUTHS = json.load(open('mouths.json'))


def _place(self, it, get_M, M_now, sw, sh):
    """Bubble sits on the side the speaker FACES, a little above mouth level; its tail
    leaves the corner nearest the speaker and points down toward the mouth, stopping
    before the face. Never covers any face (checked over the whole time it is shown)."""
    key = ('place', id(it))
    if key in self._cache:
        return self._cache[key]
    S, W, H = self.S, self.W, self.H
    bw, bh = self._comic_size(it['text'], it['sp'])
    mats = []
    for tt in (it['a'], (it['a'] + it['b']) / 2, it['b'] + 0.2):
        r = get_M(it['scene'], tt) if get_M else None
        mats.append(r[0] if r else M_now)
    Ma = mats[0]
    faces = FACES2.get(it['scene'], {})
    raw = []
    for Mx in mats:
        for who, (x0, y0, x1, y1) in faces.items():
            p0 = Mx @ np.array([x0 * sw, y0 * sh, 1.0]); p1 = Mx @ np.array([x1 * sw, y1 * sh, 1.0])
            raw.append((min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1])))
    m = 14 * S
    boxes = [(a - m, b - m, c_ + m, d + m) for a, b, c_, d in raw]
    if any(h['start'] - 0.3 < it['b'] + 0.3 and h['end'] + 0.5 > it['a'] - 0.3 for h in TL_HUDS):
        boxes.append((0, 0, 790 * S, 270 * S)); raw.append((0, 0, 790 * S, 270 * S))
    sp = it['sp']
    mk = f"{it['scene']}:{sp}"
    if mk in MOUTHS:
        mx, my, face = MOUTHS[mk]
    else:   # off-screen voice (radio): anchor point, face toward screen centre
        mx, my = ANCH.get(mk, (0.5, 0.3)); face = 1 if mx < 0.5 else -1
    px, py = Ma @ np.array([mx * sw, my * sh, 1.0])
    # speaker's own face box (screen) - tail stops at its edge
    if sp in faces:
        x0, y0, x1, y1 = faces[sp]
        q0 = Ma @ np.array([x0 * sw, y0 * sh, 1.0]); q1 = Ma @ np.array([x1 * sw, y1 * sh, 1.0])
        fb = (min(q0[0], q1[0]), min(q0[1], q1[1]), max(q0[0], q1[0]), max(q0[1], q1[1]))
    else:
        fb = (px - 5, py - 5, px + 5, py + 5)

    def hits(r, bl):
        return sum(max(0, min(r[2], b[2]) - max(r[0], b[0])) * max(0, min(r[3], b[3]) - max(r[1], b[1])) for b in bl)

    def tail_tip(bx_, by_, mirror, relaxed=False):
        u = 0.20 if not mirror else 0.80
        base = (bx_ + u * bw, by_ + bh * 0.97)
        dx, dy = px - base[0], py - base[1]
        L = math.hypot(dx, dy) + 1e-6
        if dy < (0.10 if relaxed else 0.20) * L:          # tail must clearly point DOWN
            return None
        ux, uy = dx / L, dy / L
        # distance along the ray until we enter the speaker's face box
        # tail points at the mouth and stops a little before it
        ln = min(max(L - 34 * S, 50 * S), 140 * S)
        if L - ln < 20 * S:
            ln = L - 20 * S
        if ln < 36 * S:
            return None
        return base, (base[0] + ux * ln, base[1] + uy * ln)

    # --- bubble grows OUT of the speaker's face: right beside it on the facing side ---
    own = fb
    others = [r for r in raw if not (abs(r[0] - own[0]) < 2 and abs(r[1] - own[1]) < 2)]
    csz0 = self._cache[('csz', it['text'], sp)]
    bw, bh = csz0[0], csz0[1]
    best = None
    for side in (face, -face):
        mirror = side < 0
        for gx in np.arange(-0.35, 0.9, 0.05):          # how far the bubble sits out from the face edge
            for gy in np.arange(-0.2, 1.4, 0.1):         # bubble bottom relative to mouth (in bubble heights)
                edge = own[2] if side > 0 else own[0]
                bx = edge + gx * bw if side > 0 else edge - bw - gx * bw
                by = py - bh - gy * bh - 10 * S
                if bx < 20 * S or bx + bw > W - 20 * S or by < 40 * S or by + bh > H - 170 * S:
                    continue
                u = 0.20 if not mirror else 0.80
                base = (bx + u * bw, by + bh * 0.97)
                dx, dy = px - base[0], py - base[1]
                L = math.hypot(dx, dy) + 1e-6
                if dy < 4 * S:                          # tail must not point up
                    continue
                ln = min(max(L - 22 * S, 56 * S), 120 * S)
                tip = (base[0] + dx / L * ln, base[1] + dy / L * ln)
                body = (bx, by, bx + bw + 8 * S, by + bh + 8 * S)
                own_ov = hits(body, [own])
                oth_ov = hits(body, others)
                score = own_ov * 80 + oth_ov * 2 + L * 6 + (0 if side == face else 1e12)
                if best is None or score < best[0]:
                    best = (score, bx, by, base, tip, mirror, bw, bh, csz0)
    if best is None:
        self._cache[key] = None
        return None
    _, bx, by, base, tip, mirror, bw, bh, csz = best
    self._cache[('csz', it['text'], sp)] = csz
    inv = cv2.invertAffineTransform(Ma)
    sx, sy = inv @ np.array([bx, by, 1.0])
    txs, tys = inv @ np.array([tip[0], tip[1], 1.0])
    res = dict(sx=sx, sy=sy, tx=txs, ty=tys, cx=base[0] - bx, bw=bw, bh=bh, mirror=mirror)
    self._cache[key] = res
    return res


TAG = {'MIA': ('Mia', (226, 96, 112)), 'ECHO': ('Echo', (38, 168, 196)), 'ELENA': ('Dr. Elena', (96, 120, 210)),
       'OP': ('Radio', (220, 150, 40)), 'TECH': ('Technician', (150, 110, 70))}


def _comic(self, text, sp, cx, tdx, tdy, mirror):
    """Style 4: clean white rounded bubble, soft shadow, coloured name tag on the top edge,
    tail from the bottom edge toward the speaker's mouth."""
    S = self.S
    q_ = 6 * S
    tdxq, tdyq = round(tdx / q_) * q_, round(tdy / q_) * q_
    key = ('pill', text, sp, round(cx / q_), tdxq, tdyq)
    if key in self._cache:
        return self._cache[key]
    bw, bh, lines, lh = self._cache[('csz', text, sp)]
    pad = int(150 * S)
    W_, H_ = bw + 2 * pad, bh + 2 * pad
    ox, oy = pad, pad
    rad = min(bh / 2, 40 * S)
    base_x = ox + min(max(cx, rad + 14 * S), bw - rad - 14 * S)
    half = 20 * S
    by_ = oy + bh - 2
    tip = (base_x + tdxq, oy + bh + tdyq)
    lean = 1 if tdxq >= 0 else -1
    tail = [(base_x - half, by_), (base_x + half, by_), tip]
    # shadow
    sh = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.rounded_rectangle([ox + 3 * S, oy + 7 * S, ox + bw + 3 * S, oy + bh + 7 * S], rad, fill=(0, 0, 0, 80))
    ds.polygon([(x + 3 * S, y + 7 * S) for x, y in tail], fill=(0, 0, 0, 80))
    sh = sh.filter(ImageFilter.GaussianBlur(6 * S))
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    im = Image.alpha_composite(im, sh)
    d = ImageDraw.Draw(im)
    d.polygon(tail, fill=(255, 255, 255, 250))
    d.rounded_rectangle([ox, oy, ox + bw, oy + bh], rad, fill=(255, 255, 255, 250))
    # name tag
    name, col = TAG.get(sp, (sp.title(), (120, 120, 120)))
    ft = ImageFont.truetype(KIDS, int(29 * S))
    tw_n = ft.getlength(name)
    tx0 = ox + 20 * S if not mirror else ox + bw - 20 * S - (tw_n + 28 * S)
    d.rounded_rectangle([tx0, oy - 26 * S, tx0 + tw_n + 28 * S, oy + 12 * S], 18 * S, fill=col + (255,))
    d.text((tx0 + 14 * S, oy - 25 * S), name, font=ft, fill=(255, 255, 255, 255))
    f, tr = self.f_bub, self.track_bub
    top = oy + (bh - lh * len(lines)) / 2 + 2 * S
    for i, l in enumerate(lines):
        x = ox + (bw - tw(l, f, tr)) / 2
        draw_tracked(d, (x, top + i * lh), l, f, (45, 45, 55, 255), tr)
    res = (np.asarray(im).astype(np.float32), (ox, oy), tip)
    if len(self._cache) > 900:
        keep = {k: v for k, v in self._cache.items() if k[0] in ('place', 'csz', 'sub3')}
        self._cache.clear(); self._cache.update(keep)
    self._cache[key] = res
    return res


Captions._place = _place
Captions._comic_size = _comic_size
Captions._comic = _comic
