"""Close-up split thumbnail: Mia crying | Echo's visor reflecting Mom's photo."""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
F = 'assets/fonts/'
PF, PFI, BB = F + 'playfair-display-latin-900-normal.woff', F + 'playfair-display-latin-900-italic.woff', F + 'bebas-neue-latin-400-normal.woff'
MONO = F + 'inter-latin-800-normal.woff'
W, H = 1280, 720


def crop(name, cx, cy, w):
    im = cv2.imread(f'assets/img/{name}.png'); ih, iw = im.shape[:2]
    pw = int(w * iw); ph = int(pw * H / W * 1.0)
    x0 = int(cx * iw - pw / 2); y0 = int(cy * ih - ph / 2)
    x0 = max(0, min(iw - pw, x0)); y0 = max(0, min(ih - ph, y0))
    return cv2.cvtColor(cv2.resize(im[y0:y0 + ph, x0:x0 + pw], (W, H), interpolation=cv2.INTER_LANCZOS4), cv2.COLOR_BGR2RGB)


def side(name, cx, cy, frac_h, out_w):
    im = cv2.imread(f'assets/img/{name}.png'); ih, iw = im.shape[:2]
    ph = int(frac_h * ih); pw = int(ph * out_w / H)
    x0 = max(0, min(iw - pw, int(cx * iw - pw / 2))); y0 = max(0, min(ih - ph, int(cy * ih - ph / 2)))
    return cv2.cvtColor(cv2.resize(im[y0:y0 + ph, x0:x0 + pw], (out_w, H), interpolation=cv2.INTER_LANCZOS4), cv2.COLOR_BGR2RGB).astype(np.float32)


def compose():
    lw = int(W * 0.60); rw = int(W * 0.56); ov = lw + rw - W
    mia = side('s24', 0.335, 0.42, 0.52, lw)      # Mia's tearful face
    echo = side('s04', 0.47, 0.36, 0.62, rw)      # Echo's visor reflecting Mom's photo
    out = np.zeros((H, W, 3), np.float32)
    out[:, :lw] = mia
    ramp = np.linspace(0, 1, ov)[None, :, None]
    out[:, lw - ov:lw] = mia[:, lw - ov:] * (1 - ramp) + echo[:, :ov] * ramp
    out[:, lw:] = echo[:, ov:]
    out = out.astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - 0.42 * (((xx - W / 2) / (W * 0.6)) ** 2 + ((yy - H * 0.45) / (H * 0.75)) ** 2)
    out *= np.clip(v, 0.5, 1)[..., None]
    b = cv2.GaussianBlur(out, (0, 0), 1.2); out = cv2.addWeighted(out, 1.45, b, -0.45, 0)
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    img = ImageEnhance.Color(img).enhance(1.2); img = ImageEnhance.Contrast(img).enhance(1.1)
    img = img.convert('RGBA')
    g = np.zeros((H, W), np.float32); g[:, :] = np.clip((np.arange(H)[:, None] - H * 0.52) / (H * 0.48), 0, 1) ** 1.2 * 230
    sh = Image.new('RGBA', (W, H), (6, 4, 14, 0)); sh.putalpha(Image.fromarray(g.astype(np.uint8))); img.alpha_composite(sh)
    return img


def txt(img, xy, s, font, fill, anchor='ls', stroke=8):
    shd = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shd).text((xy[0] + 5, xy[1] + 7), s, font=font, fill=(0, 0, 0, 220), anchor=anchor, stroke_width=stroke + 4, stroke_fill=(0, 0, 0, 220))
    img.alpha_composite(shd.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(img).text(xy, s, font=font, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(18, 10, 20, 255))


def tag(img, x, y, s):
    f = ImageFont.truetype(MONO, 30); d = ImageDraw.Draw(img); w = d.textlength(s, font=f)
    box = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle([x, y, x + w + 40, y + 56], 10, fill=(20, 6, 8, 225), outline=(255, 80, 70, 255), width=3)
    img.alpha_composite(box); ImageDraw.Draw(img).text((x + 20, y + 12), s, font=f, fill=(255, 95, 85, 255))


# C1 - elegant serif
c = compose()
txt(c, (60, H - 150), 'HE LIED', ImageFont.truetype(PF, 150), (255, 244, 222, 255))
txt(c, (66, H - 52), 'for five years.', ImageFont.truetype(PFI, 78), (246, 200, 120, 255), stroke=6)
tag(c, W - 330, 40, 'LIE DETECTED')
c.convert('RGB').save('brand/thumbnail_C_he_lied.jpg', quality=95)

# C2 - bold condensed
c = compose()
txt(c, (58, H - 60), 'HE LIED FOR 5 YEARS', ImageFont.truetype(BB, 168), (255, 236, 160, 255), stroke=7)
tag(c, W - 330, 40, 'LIE DETECTED')
c.convert('RGB').save('brand/thumbnail_D_he_lied_bold.jpg', quality=95)
print('ok')
