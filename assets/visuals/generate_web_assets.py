"""Generate non-placeholder web visuals for StevenAiDigest.

Overwrites files in assets/visuals/web:
- chart-slide.webp
- editorial-square.webp
- memo-loop-poster.webp
- memo-loop-poster.jpg
- memo-loop.mp4

Design goal: professional, brand-consistent, no template placeholder text.
"""

from __future__ import annotations

import math
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[2]  # steven-ai-digest/
WEB = ROOT / "assets" / "visuals" / "web"
FFMPEG = os.environ.get(
    "FFMPEG_BIN",
    r"C:\Users\Administrator\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe",
)


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    # Use Windows system fonts.
    candidates = [
        r"C:\\Windows\\Fonts\\segoeuib.ttf" if bold else r"C:\\Windows\\Fonts\\segoeui.ttf",
        r"C:\\Windows\\Fonts\\arialbd.ttf" if bold else r"C:\\Windows\\Fonts\\arial.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()


def gradient_bg(w: int, h: int) -> Image.Image:
    # Subtle dark-to-deeper gradient with a couple of soft color blooms.
    base = Image.new("RGB", (w, h), (10, 14, 26))
    g = Image.new("RGB", (w, h))
    px = g.load()
    for y in range(h):
        t = y / (h - 1)
        # vertical gradient
        r = int(12 + (6 * (1 - t)))
        g2 = int(16 + (10 * (1 - t)))
        b = int(30 + (18 * (1 - t)))
        for x in range(w):
            px[x, y] = (r, g2, b)
    base = Image.blend(base, g, 0.65)

    # bloom 1 (violet)
    bloom1 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(bloom1)
    d.ellipse((int(w * 0.05), int(-h * 0.35), int(w * 0.75), int(h * 0.55)), fill=(124, 92, 255, 85))
    bloom1 = bloom1.filter(ImageFilter.GaussianBlur(80))

    # bloom 2 (cyan)
    bloom2 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(bloom2)
    d.ellipse((int(w * 0.45), int(-h * 0.25), int(w * 1.15), int(h * 0.65)), fill=(0, 212, 255, 55))
    bloom2 = bloom2.filter(ImageFilter.GaussianBlur(90))

    out = base.convert("RGBA")
    out = Image.alpha_composite(out, bloom1)
    out = Image.alpha_composite(out, bloom2)
    return out.convert("RGBA")


def draw_brand(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, subtitle: str = "DAILY MEMO"):
    f_brand = _load_font(26, bold=True)
    f_sub = _load_font(14, bold=True)
    draw.text((x, y), "STEVEN AI DIGEST", font=f_brand, fill=(235, 242, 255, 230))
    draw.text((x, y + 30), subtitle, font=f_sub, fill=(168, 179, 199, 230))


def make_chart_slide(path: Path, w: int = 1200, h: int = 675):
    img = gradient_bg(w, h)
    draw = ImageDraw.Draw(img)

    # card
    pad = 70
    card = (pad, pad, w - pad, h - pad)
    draw.rounded_rectangle(card, radius=30, outline=(255, 255, 255, 40), width=2, fill=(255, 255, 255, 10))

    draw_brand(draw, pad + 32, pad + 26, w)

    # chart area
    cx0, cy0 = pad + 32, pad + 120
    cx1, cy1 = w - pad - 32, h - pad - 36
    draw.rounded_rectangle((cx0, cy0, cx1, cy1), radius=22, outline=(255, 255, 255, 35), width=2, fill=(0, 0, 0, 0))

    # axes
    axc = (255, 255, 255, 30)
    draw.line((cx0 + 30, cy1 - 40, cx1 - 20, cy1 - 40), fill=axc, width=2)
    draw.line((cx0 + 30, cy0 + 20, cx0 + 30, cy1 - 40), fill=axc, width=2)

    # curve
    pts = []
    for i in range(10):
        t = i / 9
        x = (cx0 + 40) + t * (cx1 - cx0 - 80)
        y = (cy1 - 55) - (math.log1p(6 * t) / math.log1p(6)) * (cy1 - cy0 - 120)
        y += math.sin(t * 4) * 8
        pts.append((x, y))

    # glow line
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line(pts, fill=(124, 92, 255, 180), width=10, joint="curve")
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)
    draw.line(pts, fill=(200, 190, 255, 220), width=4, joint="curve")

    # dots
    for (x, y) in pts[::2]:
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(0, 212, 255, 200), outline=(255, 255, 255, 90), width=1)

    # footer small
    f_small = _load_font(14)
    draw.text((cx0 + 36, cy1 - 32), "Source: primary links in edition", font=f_small, fill=(168, 179, 199, 200))

    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, "WEBP", quality=88, method=6)


def make_editorial_square(path: Path, w: int = 1080, h: int = 1080):
    img = gradient_bg(w, h)
    draw = ImageDraw.Draw(img)

    # frame
    pad = 70
    draw.rounded_rectangle((pad, pad, w - pad, h - pad), radius=32, outline=(255, 255, 255, 45), width=2, fill=(255, 255, 255, 10))

    # abstract "editorial" shapes (no prompt text)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle((pad + 60, pad + 120, w - pad - 80, h - pad - 140), radius=26, fill=(0, 0, 0, 35), outline=(255, 255, 255, 25), width=2)
    od.ellipse((pad + 110, pad + 170, pad + 360, pad + 420), fill=(124, 92, 255, 55))
    od.ellipse((w - pad - 420, pad + 260, w - pad - 150, pad + 530), fill=(0, 212, 255, 40))
    overlay = overlay.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    draw_brand(draw, pad + 42, pad + 34, w, subtitle="EDITORIAL")

    f_h = _load_font(44, bold=True)
    f_s = _load_font(20)
    draw.text((pad + 42, h - pad - 170), "Daily signal.", font=f_h, fill=(232, 237, 247, 235))
    draw.text((pad + 42, h - pad - 120), "Professional visuals. Source backed.", font=f_s, fill=(168, 179, 199, 220))

    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, "WEBP", quality=90, method=6)


def make_poster(path_webp: Path, path_jpg: Path, w: int = 1080, h: int = 1080):
    img = gradient_bg(w, h)
    draw = ImageDraw.Draw(img)

    # gradient panel
    pad = 80
    draw.rounded_rectangle((pad, pad, w - pad, h - pad), radius=34, outline=(255, 255, 255, 40), width=2, fill=(255, 255, 255, 10))

    # top ribbon
    ribbon_h = int((h - 2 * pad) * 0.42)
    ribbon = Image.new("RGBA", (w - 2 * pad, ribbon_h), (124, 92, 255, 80))
    rib2 = Image.new("RGBA", (w - 2 * pad, ribbon_h), (0, 212, 255, 50))
    rib2 = rib2.filter(ImageFilter.GaussianBlur(40))
    ribbon = Image.alpha_composite(ribbon, rib2)
    img.paste(ribbon, (pad, pad), ribbon)

    draw_brand(draw, pad + 42, pad + 34, w)

    f_h = _load_font(54, bold=True)
    f_s = _load_font(22)
    draw.text((pad + 42, pad + ribbon_h + 70), "Signal over noise.", font=f_h, fill=(232, 237, 247, 240))
    draw.text((pad + 42, pad + ribbon_h + 140), "Daily memo format: thesis → evidence → implication → action", font=f_s, fill=(168, 179, 199, 230))

    path_webp.parent.mkdir(parents=True, exist_ok=True)
    img_rgb = img.convert("RGB")
    img_rgb.save(path_webp, "WEBP", quality=92, method=6)
    img_rgb.save(path_jpg, "JPEG", quality=90, optimize=True)


def make_video(out_mp4: Path, poster_webp: Path):
    # Create a subtle zoompan loop from the poster.
    tmp_png = out_mp4.with_suffix(".png")
    Image.open(poster_webp).convert("RGB").save(tmp_png)

    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        FFMPEG,
        "-y",
        "-loop",
        "1",
        "-i",
        str(tmp_png),
        "-t",
        "6",
        "-vf",
        "zoompan=z='min(1.08,1+on*0.0006)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=180:fps=30,format=yuv420p",
        "-movflags",
        "+faststart",
        str(out_mp4),
    ]
    subprocess.check_call(cmd)
    try:
        tmp_png.unlink(missing_ok=True)
    except Exception:
        pass


def main():
    WEB.mkdir(parents=True, exist_ok=True)

    chart = WEB / "chart-slide.webp"
    editorial = WEB / "editorial-square.webp"
    poster_webp = WEB / "memo-loop-poster.webp"
    poster_jpg = WEB / "memo-loop-poster.jpg"
    video = WEB / "memo-loop.mp4"

    make_chart_slide(chart)
    make_editorial_square(editorial)
    make_poster(poster_webp, poster_jpg)
    make_video(video, poster_webp)

    print("Wrote:")
    for p in [chart, editorial, poster_webp, poster_jpg, video]:
        print(" -", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
