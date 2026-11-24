"""YouTube thumbnails 1280x720 for The Robot That Learned to Lie."""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
F = 'assets/fonts/'
BOLD, MONO = F + 'fredoka-latin-600-normal.woff', F + 'inter-latin-800-normal.woff'
W, H = 1280, 720


def base(name, box, sat=1.25, con=1.12):
    im = Image.open(f'assets/img/{name}.png').convert('RGB')
    iw, ih = im.size; x0, y0, x1 = box; x0, x1 = int(x0 * iw), int(x1 * iw); y0 = int(y0 * ih)
    h = int((x1 - x0) * 9 / 16); im = im.crop((x0, y0, x1, y0 + h)).resize((W, H), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(sat); im = ImageEnhance.Contrast(im).enhance(con)
    a = np.asarray(im).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]; v = 1 - 0.38 * (((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)
    a *= np.clip(v, 0.55, 1)[..., None]
    b = cv2.GaussianBlur(a, (0, 0), 1.0); a = cv2.addWeighted(a, 1.4, b, -0.4, 0)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


def outlined(img, xy, text, font, fill, stroke=10, anchor='la', shadow=True):
    d = ImageDraw.Draw(img)
    if shadow:
        sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((xy[0] + 6, xy[1] + 8), text, font=font, fill=(0, 0, 0, 200), anchor=anchor,
                                 stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(img).text(xy, text, font=font, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(20, 16, 30, 255))


def hud(img, x, y, lines, scale=1.0):
    f1 = ImageFont.truetype(MONO, int(30 * scale)); f0 = ImageFont.truetype(MONO, int(18 * scale))
    d = ImageDraw.Draw(img)
    w = max(d.textlength(l, font=f1) for l in lines) + 44 * scale; h = (40 + 42 * len(lines)) * scale
    box = Image.new('RGBA', img.size, (0, 0, 0, 0)); db = ImageDraw.Draw(box)
    db.rounded_rectangle([x, y, x + w, y + h], int(10 * scale), fill=(8, 14, 24, 215), outline=(90, 220, 240, 230), width=3)
    img.alpha_composite(box)
    d = ImageDraw.Draw(img)
    d.text((x + 22 * scale, y + 12 * scale), 'ECHO-07 // DIAGNOSTIC', font=f0, fill=(110, 200, 220, 255))
    for i, l in enumerate(lines):
        d.text((x + 22 * scale, y + (36 + 42 * i) * scale), l, font=f1, fill=(255, 90, 80, 255) if i == 0 else (150, 235, 250, 255))


# A: the lie (Echo looks at Mom's photo)
a = base('s04', (0.0, 0.02, 1.0))
grad = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = np.zeros((H, W), np.float32)
g[:, :] = np.clip((np.arange(H)[:, None] - H * 0.55) / (H * 0.45), 0, 1) * 200
grad.putalpha(Image.fromarray(g.astype(np.uint8))); a.alpha_composite(grad)
hud(a, 40, 36, ['WARNING:', 'STATEMENT IS FALSE'], 1.0)
outlined(a, (W / 2, H - 52), 'HIS KINDEST LIE', ImageFont.truetype(BOLD, 118), (255, 236, 190, 255), anchor='ms')
a.convert('RGB').save('brand/thumbnail_A_kindest_lie.jpg', quality=95)

# B: the bridge (Stop lying!)
b = base('s38', (0.08, 0.05, 0.98), sat=1.3)
outlined(b, (W * 0.60, 150), 'STOP LYING!', ImageFont.truetype(BOLD, 128), (255, 236, 200, 255), anchor='ms')
hud(b, 36, H - 178, ['BATTERY: 2%', 'SHUTDOWN IMMINENT'], 0.9)
b.convert('RGB').save('brand/thumbnail_B_stop_lying.jpg', quality=95)
print('ok')
