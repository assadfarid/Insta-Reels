"""Moonlit Tales kit from the painted art (brand/src/).  python3 brand/make_brand2.py"""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import importlib.util
spec = importlib.util.spec_from_file_location('b1', 'brand/make_brand.py')
F = 'assets/fonts/'
SERIF, HAND, ROUND = F + 'amatic-sc-latin-700-normal.woff', F + 'amatic-sc-latin-700-normal.woff', F + 'fredoka-latin-600-normal.woff'
GOLD, CREAM, CYAN = (238, 202, 130), (250, 240, 220), (190, 225, 250)
OUT = 'brand/'
logo_art = Image.open('brand/src/logo_art.png').convert('RGB')
art = Image.open('brand/src/banner_art.png').convert('RGB')


def up(img, size):
    """Lanczos upscale + gentle sharpen."""
    a = cv2.resize(np.asarray(img), size, interpolation=cv2.INTER_LANCZOS4)
    b = cv2.GaussianBlur(a, (0, 0), 1.2)
    return Image.fromarray(cv2.addWeighted(a, 1.35, b, -0.35, 0)).convert('RGBA')


def ornament(w):
    h = max(40, w // 9); a = np.zeros((h, w), np.float32); cy = h // 2; gap = int(h * 0.55)
    xs = np.arange(w); dd = np.abs(xs - w / 2); half = w / 2
    al = np.clip((dd - gap) / (h * 0.2), 0, 1) * np.clip(1 - (dd - gap) / (half - gap), 0, 1) ** 0.8
    th = max(1, h // 26)
    for k, wt in ((0, 1.0), (1, 0.5), (2, 0.15)):
        for sg in ((0,) if k == 0 else (-1, 1)):
            y = cy + sg * (th + k - 1) if k else cy
            a[y] = np.maximum(a[y], al * wt)
    arr = np.zeros((h, w, 4), np.uint8); arr[..., :3] = GOLD; arr[..., 3] = (a * 255).astype(np.uint8)
    im = Image.fromarray(arr, 'RGBA'); d = ImageDraw.Draw(im)
    r = h * 0.16
    d.polygon([(w / 2, cy - r), (w / 2 + r, cy), (w / 2, cy + r), (w / 2 - r, cy)], fill=GOLD + (255,))
    for sx in (-1, 1):
        x = w / 2 + sx * h * 0.42; r2 = h * 0.08
        d.polygon([(x, cy - r2), (x + r2, cy), (x, cy + r2), (x - r2, cy)], fill=GOLD + (230,))
    return im


def text(d, cx, y, s, font, fill, glow_im=None):
    w = d.textlength(s, font=font)
    if glow_im is not None:
        g = Image.new('RGBA', glow_im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text((cx - w / 2, y), s, font=font, fill=(10, 16, 45, 210))
        glow_im.alpha_composite(g.filter(ImageFilter.GaussianBlur(14)))
        d = ImageDraw.Draw(glow_im)
    d.text((cx - w / 2 + 3, y + 4), s, font=font, fill=(0, 0, 0, 110))
    d.text((cx - w / 2, y), s, font=font, fill=fill)


def title_block(img, cx, cy, scale):
    d = ImageDraw.Draw(img)
    ft = ImageFont.truetype(SERIF, int(230 * scale)); fs = ImageFont.truetype(HAND, int(84 * scale))
    text(d, cx, cy - 190 * scale, 'Moonlit Tales', ft, (246, 196, 82, 255), img)
    text(ImageDraw.Draw(img), cx, cy + 62 * scale, 'Bedtime stories for little dreamers', fs, CREAM + (255,), img)


# 1. logo 800 (+ round preview, watermark)
lg = up(logo_art, (800, 800)); lg.convert('RGB').save(OUT + 'moonlit_tales_logo_800.png')
circ = Image.new('L', (800, 800), 0); ImageDraw.Draw(circ).ellipse([0, 0, 799, 799], fill=255)
rl = Image.new('RGBA', (800, 800), (0, 0, 0, 0)); rl.paste(lg, (0, 0), circ); rl.save(OUT + 'moonlit_tales_logo_round_preview.png')
wm = rl.resize((150, 150), Image.LANCZOS); wm.save(OUT + 'moonlit_tales_watermark_150.png')

# 2. banner 2560x1440: title in the open sky, inside the phone-safe area, left of the moon
W, H = 2560, 1440
ban = up(art, (W, H)); title_block(ban, 1010, H / 2, 1.0)
ban.convert('RGB').save(OUT + 'moonlit_tales_banner_2560x1440.jpg', quality=94)
pv = ban.copy(); dp = ImageDraw.Draw(pv)
dp.rectangle([(W - 1546) / 2, (H - 423) / 2, (W + 1546) / 2, (H + 423) / 2], outline=(255, 80, 80, 255), width=6)
pv.convert('RGB').resize((1280, 720)).save(OUT + 'banner_safe_area_preview.jpg', quality=88)

# 3. intro card 1920x1080
W, H = 1920, 1080
ic = up(art, (W, H)); d = ImageDraw.Draw(ic)
text(d, 760, H / 2 - 190, 'Moonlit Tales', ImageFont.truetype(SERIF, 210), (246, 196, 82, 255), ic)

text(ImageDraw.Draw(ic), 760, H / 2 + 50, 'presents', ImageFont.truetype(HAND, 84), CREAM + (255,), ic)
ic.convert('RGB').save(OUT + 'moonlit_tales_intro_card_1920x1080.jpg', quality=94)

# 4. end screen 1920x1080: softened art, two video slots on the left, subscribe spot under the moon
es = up(art, (W, H))
dim = Image.new('RGBA', (W, H), (8, 14, 40, 0)); a = np.zeros((H, W), np.float32)
a[:, :] = np.clip(1.15 - np.linspace(0, 1, W)[None, :] * 1.2, 0.15, 0.75) * 255
dim.putalpha(Image.fromarray(a.astype(np.uint8))); es.alpha_composite(dim)
d = ImageDraw.Draw(es)
text(d, 600, 50, 'Thank you for watching', ImageFont.truetype(SERIF, 110), (246, 196, 82, 255), es)

d = ImageDraw.Draw(es)
for y in (255, 610):
    d.rounded_rectangle([340, y, 340 + 520, y + 293], 22, outline=GOLD + (220,), width=4)
text(d, 600, 975, 'A new bedtime story every week', ImageFont.truetype(HAND, 66), CREAM + (255,), es)
es.convert('RGB').save(OUT + 'moonlit_tales_end_screen_1920x1080.jpg', quality=94)

# 5. ornament
ornament(1600).save(OUT + 'moonlit_tales_ornament.png')
print('done')
