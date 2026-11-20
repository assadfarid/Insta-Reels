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
        self.f_bub = ImageFont.truetype(KIDS, int(39 * S))
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
            draw_tracked(dg, (x, y), l, f, (120, 232, 92, 255), tr)
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
        lines = wrap(text, f, 520 * S, tr)
        lh = int(46 * S)
        tw_ = max(tw(l, f, tr) for l in lines)
        bw, bh = int(tw_ + 84 * S), int(lh * len(lines) + 58 * S)
        self._cache[key] = (bw, bh, lines, lh)
    return self._cache[key][:2]


def _place(self, it, get_M, M_now, sw, sh):
    """Choose the bubble position ONCE per line (at its start time) so it never covers any
    face (all characters, incl. hair) for the whole time it is on screen."""
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
    m = 16 * S
    raw = []
    for Mx in mats:
        for who, (x0, y0, x1, y1) in faces.items():
            p0 = Mx @ np.array([x0 * sw, y0 * sh, 1.0]); p1 = Mx @ np.array([x1 * sw, y1 * sh, 1.0])
            raw.append((min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1])))
    boxes = [(a - m, b - m, c_ + m, d + m) for a, b, c_, d in raw]
    hud = any(h['start'] - 0.3 < it['b'] + 0.3 and h['end'] + 0.5 > it['a'] - 0.3 for h in TL_HUDS)
    if hud:
        boxes.append((0, 0, 790 * S, 270 * S))
        raw.append((0, 0, 790 * S, 270 * S))
    # speaker target: top-centre of their head box (or the anchor for off-face voices like the radio)
    sp = it['sp']
    if sp in faces:
        x0, y0, x1, y1 = faces[sp]
        q0 = Ma @ np.array([x0 * sw, y0 * sh, 1.0]); q1 = Ma @ np.array([x1 * sw, y1 * sh, 1.0])
        fx0, fy0, fx1, fy1 = q0[0], q0[1], q1[0], q1[1]
    else:
        ax, ay = ANCH.get(f"{it['scene']}:{sp}", (0.5, 0.3))
        q = Ma @ np.array([ax * sw, ay * sh, 1.0])
        fx0, fy0, fx1, fy1 = q[0] - 10 * S, q[1] - 10 * S, q[0] + 10 * S, q[1] + 10 * S
    hx = (fx0 + fx1) / 2
    hy = fy0
    # possible tail targets just OUTSIDE the speaker's head box: top-centre, left side, right side
    targets = [(hx, fy0 - 6 * S)]
    for fr in (0.3, 0.5, 0.7):
        targets += [(fx0 - 8 * S, fy0 + (fy1 - fy0) * fr), (fx1 + 8 * S, fy0 + (fy1 - fy0) * fr)]

    def hits(r, bl):
        return sum(max(0, min(r[2], b[2]) - max(r[0], b[0])) * max(0, min(r[3], b[3]) - max(r[1], b[1])) for b in bl)

    def tail_for(x, y):
        best_t = None
        for k, (gx, gy) in enumerate(targets):
            bxc = min(max(gx, x + bw * 0.16), x + bw * 0.84)
            by_ = y + bh
            vx, vy = gx - bxc, gy - by_
            if vy < 18 * S:
                continue
            L = math.hypot(vx, vy)
            if L > (650 * S if sp in faces else 4000 * S):
                continue
            ux, uy = vx / L, vy / L
            if uy < 0.3:
                continue
            ln = min(L, 130 * S)
            cand = (L + (0 if k == 0 else 60 * S), bxc, (bxc + ux * ln, by_ + uy * ln))
            if best_t is None or cand[0] < best_t[0]:
                best_t = cand
        return None if best_t is None else best_t[1:]

    best = None
    step_x, step_y = 22 * S, 18 * S
    y = 28 * S
    while y <= H - bh - 175 * S:
        x = 36 * S
        while x <= W - bw - 36 * S:
            tl = tail_for(x, y)
            if tl is not None:
                bxc, (tx, ty) = tl
                body = (x - 4 * S, y - 4 * S, x + bw + 12 * S, y + bh + 12 * S)
                tailr = (min(bxc - 30 * S, tx) , y + bh, max(bxc + 30 * S, tx), ty)
                core = (x, y, x + bw + 10 * S, y + bh + 8 * S)
                ov = hits(core, raw) * 50 + hits(body, boxes) * 0.2 + hits(tailr, raw) * 50
                ideal_y = hy - 70 * S - bh
                score = ov * 1000 + math.hypot((x + bw / 2) - hx, (y - ideal_y)) + abs(tx - hx) * 0.3
                if best is None or score < best[0]:
                    best = (score, x, y, bxc, tx, ty)
            x += step_x
        y += step_y
    if best is None:
        self._cache[key] = None
        return None
    _, x, y, bxc, tx, ty = best
    inv = cv2.invertAffineTransform(Ma)
    sx, sy = inv @ np.array([x, y, 1.0])
    txs, tys = inv @ np.array([tx, ty, 1.0])
    res = dict(sx=sx, sy=sy, tx=txs, ty=tys, cx=bxc - x, bw=bw, bh=bh, mirror=hx > x + bw / 2)
    self._cache[key] = res
    return res


def _comic(self, text, sp, cx, tdx, tdy, mirror):
    """Panel bubble like the reference: the side nearest the speaker is SHORT (narrow),
    the far side TALL; soft corners, thin ink outline, hard shadow right+bottom, sharp tail."""
    S = self.S
    q = 6 * S
    cxq, tdxq, tdyq = round(cx / q) * q, round(tdx / q) * q, round(tdy / q) * q
    key = ('panel3', text, cxq, tdxq, tdyq, mirror)
    if key in self._cache:
        return self._cache[key]
    bw, bh, lines, lh = self._cache[('csz', text, sp)]
    pad = int(120 * S)
    W_, H_ = bw + 2 * pad, bh + 2 * pad
    ox, oy = pad, pad
    rise = min(0.075 * bw, 0.26 * bh)    # top edge rises toward the far side
    drop = min(0.05 * bw, 0.17 * bh)     # bottom edge drops toward the far side
    # built with the NARROW side on the left; mirrored when the speaker is on the right
    TL = (0, rise); TR = (bw, 0); BR = (bw, bh); BL = (0, bh - drop)
    r = min(24 * S, bh * 0.26)

    def corner(prev, cur, nxt):
        d1 = math.hypot(cur[0] - prev[0], cur[1] - prev[1]); d2 = math.hypot(nxt[0] - cur[0], nxt[1] - cur[1])
        a = (cur[0] + (prev[0] - cur[0]) * r / d1, cur[1] + (prev[1] - cur[1]) * r / d1)
        b = (cur[0] + (nxt[0] - cur[0]) * r / d2, cur[1] + (nxt[1] - cur[1]) * r / d2)
        return [((1 - u) ** 2 * a[0] + 2 * (1 - u) * u * cur[0] + u * u * b[0],
                 (1 - u) ** 2 * a[1] + 2 * (1 - u) * u * cur[1] + u * u * b[1]) for u in [k / 8 for k in range(9)]]

    body = corner(BL, TL, TR) + corner(TL, TR, BR) + corner(TR, BR, BL) + corner(BR, BL, TL)
    if mirror:
        body = [(bw - x, y) for x, y in body][::-1]
        ybot = lambda x: bh - drop * (x / bw)          # mirrored bottom edge (narrow on right)
    else:
        ybot = lambda x: bh - drop * (1 - x / bw)
    body = [(ox + x, oy + y) for x, y in body]
    # tail: base on the bottom edge at cx, tip toward the speaker
    half = min(max(bw * 0.06, 20 * S), 30 * S)
    xl, xr = cxq - half, cxq + half
    b_l = (ox + xl, oy + ybot(xl) - 1); b_r = (ox + xr, oy + ybot(xr) - 1)
    tip = (ox + cxq + tdxq, oy + ybot(cxq) + tdyq)
    # insert tail into the body outline on the bottom edge
    poly = None
    for i in range(len(body)):
        p, n = body[i], body[(i + 1) % len(body)]
        if p[1] > oy + bh * 0.6 and n[1] > oy + bh * 0.6 and min(p[0], n[0]) <= ox + cxq <= max(p[0], n[0]):
            if p[0] > n[0]:   # edge runs right -> left
                ins = [b_r, tip, b_l]
            else:
                ins = [b_l, tip, b_r]
            poly = body[:i + 1] + ins + body[i + 1:]
            break
    if poly is None:
        poly = body
    ow = max(2, int(3.4 * S))
    sx_, sy_ = 10 * S, 8 * S
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(x + sx_, y + sy_) for x, y in poly], fill=INK + (255,))
    d.polygon(poly, fill=(255, 255, 255, 255), outline=INK + (255,), width=ow)
    f, tr = self.f_bub, self.track_bub
    top = oy + (bh - lh * len(lines)) / 2 - 3 * S + (rise - drop) * 0.2
    for i, l in enumerate(lines):
        x = ox + (bw - tw(l, f, tr)) / 2
        draw_tracked(d, (x, top + i * lh), l, f, INK + (255,), tr)
    res = (np.asarray(im).astype(np.float32), (ox, oy), tip)
    if len(self._cache) > 900:
        keep = {k: v for k, v in self._cache.items() if k[0] in ('place', 'csz', 'sub3')}
        self._cache.clear(); self._cache.update(keep)
    self._cache[key] = res
    return res


Captions._place = _place
Captions._comic_size = _comic_size
Captions._comic = _comic
