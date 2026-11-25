"""Sharp channel banner from the high-res art with the moon-child removed (logo already has it)."""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
AM = 'assets/fonts/amatic-sc-latin-700-normal.woff'
GOLD, CREAM = (246, 196, 82, 255), (250, 240, 220, 255)
W, H = 2560, 1440
src = cv2.cvtColor(cv2.imread('brand/src/banner_art_hires_nomoon.png'), cv2.COLOR_BGR2RGB)
a = cv2.resize(src, (W, H), interpolation=cv2.INTER_LANCZOS4)
b = cv2.GaussianBlur(a, (0, 0), 1.0); a = cv2.addWeighted(a, 1.3, b, -0.3, 0)
img = Image.fromarray(a).convert('RGBA')


def text(img, cx, y, s, font, fill):
    w = ImageDraw.Draw(img).textlength(s, font=font)
    g = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).text((cx - w / 2, y), s, font=font, fill=(10, 16, 45, 230))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(img); d.text((cx - w / 2 + 3, y + 4), s, font=font, fill=(0, 0, 0, 120)); d.text((cx - w / 2, y), s, font=font, fill=fill)


ft, fs = ImageFont.truetype(AM, 210), ImageFont.truetype(AM, 76)
d0 = ImageDraw.Draw(img)
bt = d0.textbbox((0, 0), 'Moonlit Tales', font=ft); bs = d0.textbbox((0, 0), 'Bedtime stories for little dreamers', font=fs)
gap = 50; block = (bt[3] - bt[1]) + gap + (bs[3] - bs[1]); ytop = H / 2 - block / 2
text(img, W / 2, ytop - bt[1], 'Moonlit Tales', ft, GOLD)
text(img, W / 2, ytop + (bt[3] - bt[1]) + gap - bs[1], 'Bedtime stories for little dreamers', fs, CREAM)
img.convert('RGB').save('brand/moonlit_tales_banner_2560x1440.jpg', quality=95)
f = ImageFont.truetype('assets/fonts/inter-latin-800-normal.woff', 26)
s = Image.new('RGB', (1000, 1060), (28, 28, 28)); d = ImageDraw.Draw(s); bb = img.convert('RGB')
d.text((20, 8), 'TV (full image)', font=f, fill=(255, 230, 120)); s.paste(bb.resize((960, 540)), (20, 44))
d.text((20, 600), 'Desktop (middle strip)', font=f, fill=(255, 230, 120)); s.paste(bb.crop((0, (H - 423) // 2, W, (H + 423) // 2)).resize((960, 159)), (20, 636))
d.text((20, 815), 'Phone (centre only)', font=f, fill=(255, 230, 120)); s.paste(bb.crop(((W - 1546) // 2, (H - 423) // 2, (W + 1546) // 2, (H + 423) // 2)).resize((560, 153)), (20, 851))
s.save('brand/banner_device_preview.jpg', quality=90)
print('ok')
