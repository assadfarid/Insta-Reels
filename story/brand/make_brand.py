"""Moonlit Tales brand assets (procedural watercolour look, film fonts).  python3 brand/make_brand.py"""
import math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont

F = 'assets/fonts/'
SERIF = F + 'cormorant-garamond-latin-600-normal.woff'
ITAL = F + 'cormorant-garamond-latin-500-italic.woff'
HAND = F + 'caveat-latin-600-normal.woff'
ROUND = F + 'fredoka-latin-600-normal.woff'
NAVY_TOP, NAVY_BOT = np.array([14, 20, 46]), np.array([38, 46, 92])
GOLD, CREAM, CYAN = (238, 202, 130), (250, 240, 220), (140, 225, 245)
OUT = 'brand/'
rng = np.random.default_rng(7)


def paper(w, h, strength=10):
    """Watercolour paper grain + soft blotches."""
    n = rng.normal(0, 1, (h // 4, w // 4)).astype(np.float32)
    n = cv2.GaussianBlur(cv2.resize(n, (w, h)), (0, 0), 18) * strength
    g = rng.normal(0, 3.5, (h, w)).astype(np.float32)
    return n + g


def sky(w, h, glow=None):
    y = np.linspace(0, 1, h)[:, None, None]
    img = NAVY_TOP * (1 - y) + NAVY_BOT * y
    img = np.repeat(img, w, axis=1).astype(np.float32)
    img += paper(w, h)[..., None] * np.array([0.6, 0.7, 1.0])
    if glow:
        gx, gy, r = glow
        yy, xx = np.mgrid[0:h, 0:w]
        d = np.sqrt((xx - gx) ** 2 + (yy - gy) ** 2)
        img += (np.exp(-(d / r) ** 2) * 70)[..., None] * np.array([1.0, 0.85, 0.55])
    return img


def stars(img, n, area=None, seed=1):
    h, w = img.shape[:2]; r = np.random.default_rng(seed)
    lay = np.zeros((h, w), np.float32)
    x0, y0, x1, y1 = area or (0, 0, w, h)
    for _ in range(n):
        x, y = int(r.uniform(x0, x1)), int(r.uniform(y0, y1)); s = r.uniform(0.6, 2.2) * w / 1920
        cv2.circle(lay, (x, y), max(1, int(s)), float(r.uniform(0.5, 1)), -1, cv2.LINE_AA)
    glow = cv2.GaussianBlur(lay, (0, 0), 3 * w / 1920 + 1)
    img += (lay * 200 + glow * 220)[..., None] * np.array([1.0, 0.97, 0.88])
    return img


def sparkle(d, x, y, s, col):
    d.polygon([(x, y - s), (x + s * 0.28, y - s * 0.28), (x + s, y), (x + s * 0.28, y + s * 0.28),
               (x, y + s), (x - s * 0.28, y + s * 0.28), (x - s, y), (x - s * 0.28, y - s * 0.28)], fill=col)


def moon_layer(size, glow=True):
    """Gold crescent moon with soft glow, RGBA."""
    S = size; im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    m = Image.new('L', (S, S), 0); dm = ImageDraw.Draw(m)
    r = int(S * 0.36); c = S // 2
    dm.ellipse([c - r, c - r, c + r, c + r], fill=255)
    dm.ellipse([c - r + int(r * 0.55), c - r - int(r * 0.18), c + r + int(r * 0.55), c + r - int(r * 0.18)], fill=0)
    m = m.filter(ImageFilter.GaussianBlur(S * 0.004))
    shade = Image.new('RGBA', (S, S), GOLD + (255,))
    sh = np.asarray(shade).astype(np.float32)
    yy, xx = np.mgrid[0:S, 0:S]
    k = np.clip(1.08 - ((xx - c * 0.85) ** 2 + (yy - c * 0.9) ** 2) ** 0.5 / (S * 0.55), 0.78, 1.08)
    sh[..., :3] = np.clip(sh[..., :3] * k[..., None] + paper(S, S, 6)[..., None], 0, 255)
    sh[..., 3] = np.asarray(m)
    moon = Image.fromarray(sh.astype(np.uint8), 'RGBA')
    if glow:
        g = Image.new('RGBA', (S, S), (255, 214, 140, 0)); ga = np.zeros((S, S), np.float32)
        ga = cv2.GaussianBlur(np.asarray(m).astype(np.float32), (0, 0), S * 0.06) * 0.75
        g = Image.fromarray(np.dstack([np.full((S, S), 255), np.full((S, S), 214), np.full((S, S), 150), ga]).astype(np.uint8), 'RGBA')
        im = Image.alpha_composite(im, g)
    return Image.alpha_composite(im, moon)


def book_layer(w):
    """Small open storybook, cream pages with gold edge, RGBA (w x w*0.45)."""
    h = int(w * 0.45); im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lw = max(2, w // 90)
    for sx in (-1, 1):
        pts = [(w / 2, h * 0.30), (w / 2 + sx * w * 0.47, h * 0.12), (w / 2 + sx * w * 0.49, h * 0.80), (w / 2, h * 0.95)]
        d.polygon(pts, fill=CREAM + (255,), outline=GOLD + (255,))
        d.line(pts + [pts[0]], fill=GOLD + (255,), width=lw)
        for k in range(3):
            y = h * (0.38 + k * 0.14)
            d.line([(w / 2 + sx * w * 0.08, y + h * 0.04), (w / 2 + sx * w * 0.38, y - h * 0.04)], fill=(205, 190, 160, 255), width=max(1, lw // 2))
    d.line([(w / 2, h * 0.30), (w / 2, h * 0.95)], fill=GOLD + (255,), width=lw)
    return im


def centered(d, cx, y, text, font, fill, shadow=True, spacing=0):
    w = d.textlength(text, font=font)
    if shadow:
        d.text((cx - w / 2 + 3, y + 4), text, font=font, fill=(0, 0, 0, 120))
    d.text((cx - w / 2, y), text, font=font, fill=fill)


def ornament(w, emblem=True):
    """The film's gold divider with a small crescent in the middle (RGBA)."""
    h = max(40, w // 9); im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); a = np.zeros((h, w), np.float32)
    cy = h // 2; gap = int(h * 0.75); xs = np.arange(w); dd = np.abs(xs - w / 2); half = w / 2
    al = np.clip((dd - gap) / (h * 0.2), 0, 1) * np.clip(1 - (dd - gap) / (half - gap), 0, 1) ** 0.8
    th = max(1, h // 28)
    for k, wt in ((0, 1.0), (1, 0.5), (2, 0.15)):
        for sg in ((0,) if k == 0 else (-1, 1)):
            a[cy + sg * (th + k - 1) if k else cy] = np.maximum(a[cy + sg * (th + k - 1) if k else cy], al * wt)
    arr = np.zeros((h, w, 4), np.uint8); arr[..., :3] = GOLD; arr[..., 3] = (a * 255).astype(np.uint8)
    im = Image.fromarray(arr, 'RGBA'); d = ImageDraw.Draw(im)
    for sx in (-1, 1):
        x = w / 2 + sx * (gap + h * 0.12); r = h * 0.09
        d.polygon([(x, cy - r), (x + r, cy), (x, cy + r), (x - r, cy)], fill=GOLD + (255,))
    if emblem:
        m = moon_layer(int(h * 1.5), glow=True).resize((int(h * 1.2), int(h * 1.2)), Image.LANCZOS)
        im.alpha_composite(m, (int(w / 2 - m.width / 2), int(cy - m.height / 2)))
    return im


def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')


# ---------------- 1. Logo / profile picture 800x800 ----------------
S = 800
bg = sky(S, S, glow=(S * 0.5, S * 0.42, S * 0.42)); bg = stars(bg, 70, seed=3)
logo = to_img(bg)
mn = moon_layer(int(S * 0.78)); logo.alpha_composite(mn, (int(S * 0.5 - mn.width * 0.52), int(S * 0.04)))
bk = book_layer(int(S * 0.52)); logo.alpha_composite(bk, (int(S * 0.5 - bk.width / 2), int(S * 0.60)))
d = ImageDraw.Draw(logo)
for (x, y, s) in ((0.30, 0.56, 16), (0.68, 0.53, 12), (0.58, 0.47, 9), (0.40, 0.48, 7)):
    sparkle(d, S * x, S * y, s, CREAM + (240,))
circ = Image.new('L', (S, S), 0); ImageDraw.Draw(circ).ellipse([4, 4, S - 4, S - 4], fill=255)
logo.save(OUT + 'moonlit_tales_logo_800.png')
round_logo = Image.new('RGBA', (S, S), (0, 0, 0, 0)); round_logo.paste(logo, (0, 0), circ)
round_logo.save(OUT + 'moonlit_tales_logo_round_preview.png')
# watermark 150x150 (transparent, round)
round_logo.resize((150, 150), Image.LANCZOS).save(OUT + 'moonlit_tales_watermark_150.png')

# ---------------- 2. Banner 2560x1440 ----------------
W, H = 2560, 1440
bg = sky(W, H, glow=(W * 0.5 + 1040, H * 0.5 - 240, 560)); bg = stars(bg, 420, seed=5)
# hills
yy, xx = np.mgrid[0:H, 0:W]
for (base, amp, freq, ph, col) in ((0.80, 50, 2.2, 0.4, (30, 40, 70)), (0.86, 40, 3.1, 1.7, (22, 30, 56)), (0.93, 30, 4.3, 2.9, (14, 20, 40))):
    ridge = H * base + amp * np.sin(xx / W * freq * math.pi + ph) + 18 * np.sin(xx / W * 13 + ph)
    m = (yy > ridge).astype(np.float32); m = cv2.GaussianBlur(m, (0, 0), 2)[..., None]
    bg = bg * (1 - m) + (np.array(col, np.float32) + paper(W, H, 6)[..., None]) * m
ban = to_img(bg); d = ImageDraw.Draw(ban)
# cottage with warm window (left of safe area, visible on desktop/TV)
cx0, cy0 = int(W * 0.20), int(H * 0.80)
d.polygon([(cx0, cy0), (cx0 + 120, cy0), (cx0 + 120, cy0 - 80), (cx0 + 60, cy0 - 135), (cx0, cy0 - 80)], fill=(20, 26, 48, 255))
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(glow)
for wx in (cx0 + 22, cx0 + 72):
    dg.rectangle([wx, cy0 - 62, wx + 26, cy0 - 34], fill=(255, 200, 110, 255))
glow = Image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)), glow)
ban.alpha_composite(glow)
# fireflies
for i in range(26):
    x = rng.uniform(0.05, 0.95) * W; y = rng.uniform(0.80, 0.97) * H
    f = Image.new('RGBA', (40, 40), (0, 0, 0, 0)); ImageDraw.Draw(f).ellipse([16, 16, 24, 24], fill=(255, 230, 140, 255))
    ban.alpha_composite(f.filter(ImageFilter.GaussianBlur(4)), (int(x), int(y)))
mn = moon_layer(560); ban.alpha_composite(mn, (int(W * 0.5 + 760), int(H * 0.5 - 520)))
d = ImageDraw.Draw(ban)
ft = ImageFont.truetype(SERIF, 190); fs = ImageFont.truetype(HAND, 74)
centered(d, W / 2, H / 2 - 175, 'Moonlit Tales', ft, CREAM + (255,))
orn = ornament(900); ban.alpha_composite(orn, (int(W / 2 - 450), int(H / 2 + 22)))
centered(d, W / 2, H / 2 + 88, 'Bedtime stories for little dreamers', fs, CYAN + (255,))
ban.convert('RGB').save(OUT + 'moonlit_tales_banner_2560x1440.jpg', quality=93)
# safe-area preview
pv = ban.copy(); dp = ImageDraw.Draw(pv)
dp.rectangle([(W - 1546) / 2, (H - 423) / 2, (W + 1546) / 2, (H + 423) / 2], outline=(255, 80, 80, 255), width=6)
dp.rectangle([(W - 2560) / 2, (H - 423) / 2, (W + 2560) / 2, (H + 423) / 2], outline=(80, 200, 255, 255), width=4)
pv.convert('RGB').resize((1280, 720)).save(OUT + 'banner_safe_area_preview.jpg', quality=88)

# ---------------- 3. Ornament (transparent) ----------------
ornament(1600).save(OUT + 'moonlit_tales_ornament.png')

# ---------------- 4. End screen 1920x1080 ----------------
W, H = 1920, 1080
bg = sky(W, H, glow=(W * 0.5, H * 0.2, 500)); bg = stars(bg, 220, seed=9)
es = to_img(bg); d = ImageDraw.Draw(es)
centered(d, W / 2, 70, 'Thank you for watching', ImageFont.truetype(SERIF, 86), CREAM + (255,))
es.alpha_composite(ornament(700), (W // 2 - 350, 185))
# placeholders (YouTube end-screen elements go on top of these)
for x in (180, 1020):
    d.rounded_rectangle([x, 330, x + 720, 330 + 405], 26, outline=GOLD + (200,), width=4)
    centered(d, x + 360, 505, 'Next story', ImageFont.truetype(ROUND, 44), (200, 190, 170, 200), shadow=False)
lg = round_logo.resize((220, 220), Image.LANCZOS); es.alpha_composite(lg, (W // 2 - 110, 790))
centered(d, W / 2, 1022, 'Subscribe for a new story every week', ImageFont.truetype(HAND, 46), CYAN + (255,))
es.convert('RGB').save(OUT + 'moonlit_tales_end_screen_1920x1080.jpg', quality=93)

# ---------------- 5. Intro card 1920x1080 ----------------
bg = sky(W, H, glow=(W * 0.5, H * 0.38, 420)); bg = stars(bg, 260, seed=11)
ic = to_img(bg); mn = moon_layer(360); ic.alpha_composite(mn, (W // 2 - 180, 120))
d = ImageDraw.Draw(ic)
centered(d, W / 2, 500, 'Moonlit Tales', ImageFont.truetype(SERIF, 150), CREAM + (255,))
ic.alpha_composite(ornament(760), (W // 2 - 380, 680))
centered(d, W / 2, 790, 'presents', ImageFont.truetype(HAND, 64), CYAN + (255,))
ic.convert('RGB').save(OUT + 'moonlit_tales_intro_card_1920x1080.jpg', quality=93)
print('done')
