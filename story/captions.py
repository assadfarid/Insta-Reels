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

    def draw(self, out, t, shot_M, hud_active):
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
            key = f"{it['scene']}:{it['sp']}"
            if it['scene'] not in shot_M or key not in ANCH:
                continue
            M, sw, sh = shot_M[it['scene']]
            ax, ay = ANCH[key]
            hx, hy = M @ np.array([ax * sw, ay * sh, 1.0])
            bw, bh = self._comic_size(it['text'], it['sp'])
            gap = 80 * S
            below = False
            bx = hx - bw * 0.35 if hx < W / 2 else hx - bw * 0.65
            by = hy - gap - bh
            if by < 30 * S:                     # no room above: put it below the head
                by = hy + gap
                below = True
            bx = min(max(bx, 40 * S), W - bw - 40 * S)
            by = min(max(by, 30 * S), H - bh - 170 * S)
            if hud_active and bx < 760 * S and by < 260 * S:
                by = 270 * S
                below = by > hy
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
            seed = (sum(map(ord, it['text'])) % 97) / 15.0
            by += math.sin((t - it['a']) * 2.1 + seed) * 3.2 * S
            bx += math.sin((t - it['a']) * 1.3 + seed * 2) * 1.6 * S
            # tail: base on the edge nearest the head, tip toward the head (limited length)
            cx = min(max(hx - bx, bw * 0.2), bw * 0.8)
            ey = 0 if below else bh
            vx, vy = hx - (bx + cx), hy - (by + ey)
            L = math.hypot(vx, vy) + 1e-6
            tl_ = min(L - 12 * S, 70 * S)
            tdx, tdy = vx / L * tl_, vy / L * tl_
            if (tdy > 0) == below:      # head is not on the tail side: short straight tail
                tdx, tdy = 0, (-40 if below else 40) * S
            arr, (px, py), tip = self._comic(it['text'], it['sp'], cx, tdx, tdy, below)
            # scale around the tail tip so the bubble grows out of the speaker
            if abs(sc - 1) > 0.01:
                img = cv2.resize(arr, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR)
            else:
                img = arr
            tipx, tipy = bx + cx + tdx, by + ey + tdy
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
        oval = sp in ('ELENA', 'OP')
        if oval:
            bw, bh = int(tw_ * 1.32 + 70 * S), int(lh * len(lines) * 1.45 + 56 * S)
        else:
            bw, bh = int(tw_ + 64 * S), int(lh * len(lines) + 44 * S)
        self._cache[key] = (bw, bh, lines, lh)
    return self._cache[key][:2]


def _body_points(self, bw, bh, oval, seed):
    S = self.S
    pts = []
    if oval:
        for k in range(120):
            a = 2 * math.pi * k / 120
            pts.append((bw / 2 + bw / 2 * math.cos(a), bh / 2 + bh / 2 * math.sin(a)))
    else:
        r = min(bh * 0.32, 34 * S)
        # slightly tilted top edge and bulging bottom, like a hand-drawn panel bubble
        corners = [(r, r, 180, 270), (bw - r, r, 270, 360), (bw - r, bh - r, 0, 90), (r, bh - r, 90, 180)]
        for (ccx, ccy, a0, a1) in corners:
            for k in range(13):
                a = math.radians(a0 + (a1 - a0) * k / 12)
                pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
        tilt = 0.035 * bh
        pts = [(x, y + tilt * (1 - x / bw) * (y < bh / 2) + 0.025 * bh * math.sin(math.pi * x / bw) * (y > bh / 2))
               for x, y in pts]
    # gentle hand-drawn wobble
    out = []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        w = 1.6 * S * math.sin(i * 0.9 + seed) + 1.0 * S * math.sin(i * 2.3 + seed * 1.7)
        dx, dy = x - bw / 2, y - bh / 2
        d = math.hypot(dx, dy) + 1e-6
        out.append((x + dx / d * w, y + dy / d * w))
    return out


def _comic(self, text, sp, cx, tdx, tdy, below):
    S = self.S
    q = 6 * S
    cxq, tdxq, tdyq = round(cx / q) * q, round(tdx / q) * q, round(tdy / q) * q
    key = ('comic', text, sp, cxq, tdxq, tdyq, below)
    if key in self._cache:
        return self._cache[key]
    bw, bh, lines, lh = self._cache[('csz', text, sp)]
    oval = sp in ('ELENA', 'OP')
    pad = int(95 * S)
    W_, H_ = bw + 2 * pad, bh + 2 * pad
    ox, oy = pad, pad
    seed = (sum(map(ord, text)) % 50) / 7.0
    body = [(ox + x, oy + y) for x, y in self._body_points(bw, bh, oval, seed)]
    ey = oy + (0 if below else bh)
    if oval:  # move the tail base onto the ellipse edge
        rel = (cxq / bw - 0.5) * 2
        ey = oy + bh / 2 + (-1 if below else 1) * bh / 2 * math.sqrt(max(0.0, 1 - min(0.95, rel * rel)))
    bx0 = ox + cxq
    half = min(max(bw * 0.07, 22 * S), 34 * S)
    inset = (14 * S) * (1 if below else -1)       # base sits slightly INSIDE the body
    b1, b2 = (bx0 - half, ey + inset), (bx0 + half, ey + inset)
    tip = (bx0 + tdxq, ey + tdyq)
    # curved comic tail: one side bows outward
    def bez(p0, c, p1, n=10):
        return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * c[0] + u * u * p1[0],
                 (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * c[1] + u * u * p1[1]) for u in [k / n for k in range(n + 1)]]
    side = 1 if tdxq >= 0 else -1
    c1 = ((b1[0] + tip[0]) / 2 - side * 12 * S, (b1[1] + tip[1]) / 2)
    c2 = ((b2[0] + tip[0]) / 2 - side * 4 * S, (b2[1] + tip[1]) / 2)
    tail = bez(b1, c1, tip) + bez(tip, c2, b2)[1:]
    ow = max(3, int(4.5 * S))
    sh = int(8 * S)
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # hard offset shadow (body + tail)
    d.polygon([(x + sh, y + sh) for x, y in body], fill=INK + (255,))
    d.polygon([(x + sh, y + sh) for x, y in tail], fill=INK + (255,))
    # body and tail with thick outline
    d.polygon(body, fill=(255, 255, 255, 255), outline=INK + (255,), width=ow)
    d.polygon(tail, fill=(255, 255, 255, 255), outline=INK + (255,), width=ow)
    # erase the body outline where the tail joins (white patch inside the tail's root)
    m_ = ow * 1.7
    d.rectangle([b1[0] + m_, ey - 2.2 * ow, b2[0] - m_, ey + 2.2 * ow], fill=(255, 255, 255, 255))
    if oval:  # halftone dots in the lower-right, clipped to the bubble
        mask = Image.new('L', (W_, H_), 0)
        ImageDraw.Draw(mask).polygon(body, fill=255)
        dots = Image.new('L', (W_, H_), 0)
        dd = ImageDraw.Draw(dots)
        step = 10 * S
        y = oy
        while y < oy + bh:
            x = ox
            while x < ox + bw:
                u = ((x - ox) / bw + (y - oy) / bh) / 2
                r = max(0.0, (u - 0.5) * 2) * 2.6 * S
                if r > 0.4:
                    dd.ellipse([x - r, y - r, x + r, y + r], fill=255)
                x += step
            y += step
        from PIL import ImageChops
        dots = ImageChops.multiply(dots, mask.filter(ImageFilter.MinFilter(int(ow * 2) | 1)))
        grey = Image.new('RGBA', (W_, H_), (150, 150, 150, 255))
        im.paste(grey, (0, 0), dots)
    # text
    f, tr = self.f_bub, self.track_bub
    top = oy + (bh - lh * len(lines)) / 2 - 4 * S
    for i, l in enumerate(lines):
        x = ox + (bw - tw(l, f, tr)) / 2
        draw_tracked(d, (x, top + i * lh), l, f, INK + (255,), tr)
    res = (np.asarray(im).astype(np.float32), (ox, oy), tip)
    if len(self._cache) > 600:
        self._cache.clear()
        self._comic_size(text, sp)
    self._cache[key] = res
    return res


Captions._comic_size = _comic_size
Captions._body_points = _body_points
Captions._comic = _comic
