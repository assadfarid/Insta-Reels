"""Channel banner from the cottage art (no moon-child; the logo already has it)."""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
AM = 'assets/fonts/amatic-sc-latin-700-normal.woff'
GOLD, CREAM = (246, 196, 82, 255), (250, 240, 220, 255)
W, H = 2560, 1440
src = cv2.cvtColor(cv2.imread('brand/src/banner_art_nomoon.png'), cv2.COLOR_BGR2RGB)
sh, sw = src.shape[:2]
NH = 1700; NW = int(sw * NH / sh)                # cottage body lands near the bottom of the phone-safe strip
big = cv2.resize(src, (NW, NH), interpolation=cv2.INTER_LANCZOS4)
b = cv2.GaussianBlur(big, (0, 0), 2.2); big = cv2.addWeighted(big, 1.45, b, -0.45, 0)
grain = np.random.default_rng(2).normal(0, 3, big.shape)
big = np.clip(big + grain, 0, 255).astype(np.uint8)
x0 = int(0.53 * NW) - 1720; y0 = 250       # cottage centred vertically in the phone-safe strip, right of centre
can = big[y0:y0 + H, x0:x0 + W].copy()
img = Image.fromarray(can).convert('RGBA')


def text(img, cx, y, s, font, fill):
    w = ImageDraw.Draw(img).textlength(s, font=font)
    g = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).text((cx - w / 2, y), s, font=font, fill=(10, 16, 45, 230))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(img); d.text((cx - w / 2 + 3, y + 4), s, font=font, fill=(0, 0, 0, 120)); d.text((cx - w / 2, y), s, font=font, fill=fill)


ft, fs = ImageFont.truetype(AM, 176), ImageFont.truetype(AM, 64)
d0 = ImageDraw.Draw(img)
bt = d0.textbbox((0, 0), 'Moonlit Tales', font=ft); bs = d0.textbbox((0, 0), 'Bedtime stories for little dreamers', font=fs)
gap = 50; block = (bt[3] - bt[1]) + gap + (bs[3] - bs[1])
ytop = H / 2 - block / 2                          # exact vertical centre of the strip every device shows
cx = 1000
text(img, cx, ytop - bt[1], 'Moonlit Tales', ft, GOLD)
text(img, cx, ytop + (bt[3] - bt[1]) + gap - bs[1], 'Bedtime stories for little dreamers', fs, CREAM)
img.convert('RGB').save('brand/moonlit_tales_banner_2560x1440.jpg', quality=94)
f = ImageFont.truetype('assets/fonts/inter-latin-800-normal.woff', 26)
s = Image.new('RGB', (1000, 1060), (28, 28, 28)); d = ImageDraw.Draw(s); b = img.convert('RGB')
d.text((20, 8), 'TV (full image)', font=f, fill=(255, 230, 120)); s.paste(b.resize((960, 540)), (20, 44))
d.text((20, 600), 'Desktop (middle strip)', font=f, fill=(255, 230, 120)); s.paste(b.crop((0, (H - 423) // 2, W, (H + 423) // 2)).resize((960, 159)), (20, 636))
d.text((20, 815), 'Phone (centre only)', font=f, fill=(255, 230, 120)); s.paste(b.crop(((W - 1546) // 2, (H - 423) // 2, (W + 1546) // 2, (H + 423) // 2)).resize((560, 153)), (20, 851))
s.save('brand/banner_device_preview.jpg', quality=90)
print('ok')
