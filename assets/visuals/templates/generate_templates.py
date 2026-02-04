from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent

BG = (9, 12, 18)          # near-black navy
INK = (244, 246, 250)     # off-white
MUTED = (160, 170, 188)   # slate
ACCENT = (122, 92, 255)   # violet
ACCENT2 = (46, 214, 163)  # mint


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    # Windows: Segoe UI is present by default.
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    try:
        return ImageFont.truetype(name, size=size)
    except OSError:
        return ImageFont.load_default()


def _radial_gradient(w: int, h: int, c0, c1, center=None, r=None) -> Image.Image:
    center = center or (int(w * 0.75), int(h * 0.25))
    r = r or int(max(w, h) * 0.85)
    base = Image.new("RGB", (w, h), c0)
    top = Image.new("RGB", (w, h), c1)

    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)

    # Draw concentric circles for a smooth-ish falloff.
    steps = 180
    for i in range(steps, 0, -1):
        t = i / steps
        alpha = int(255 * (t ** 2))
        rr = int(r * t)
        md.ellipse((center[0] - rr, center[1] - rr, center[0] + rr, center[1] + rr), fill=alpha)

    out = Image.composite(top, base, mask)
    return out


def _add_grain(img: Image.Image, amount: int = 14) -> Image.Image:
    # Subtle editorial grain.
    w, h = img.size
    noise = Image.effect_noise((w, h), 35).convert("L")
    noise = noise.filter(ImageFilter.GaussianBlur(0.6))
    noise = Image.eval(noise, lambda p: int((p - 128) * (amount / 32) + 128))
    noise_rgb = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(img, noise_rgb, 0.08)


def chart_slide(out: Path):
    w, h = 1920, 1080
    bg = _radial_gradient(w, h, BG, (22, 16, 52), center=(int(w * 0.62), int(h * 0.18)))
    bg = _add_grain(bg)

    d = ImageDraw.Draw(bg)

    # Header
    d.text((96, 72), "STEVEN AI DIGEST", font=_font(34, bold=True), fill=INK)
    d.text((96, 118), "DAILY MEMO", font=_font(18), fill=MUTED)

    # Title block
    d.text((96, 190), "Title goes here", font=_font(60, bold=True), fill=INK)
    d.text((96, 270), "Subtitle with one clean point. No hype.", font=_font(28), fill=MUTED)

    # Chart container
    left, top = 96, 360
    right, bottom = w - 96, h - 150
    d.rounded_rectangle((left, top, right, bottom), radius=28, outline=(48, 56, 72), width=2, fill=(12, 16, 24))

    # Fake axes + grid
    gx0, gy0 = left + 80, top + 70
    gx1, gy1 = right - 60, bottom - 70
    for i in range(6):
        y = gy0 + int((gy1 - gy0) * i / 5)
        d.line((gx0, y, gx1, y), fill=(28, 34, 46), width=1)
    for i in range(7):
        x = gx0 + int((gx1 - gx0) * i / 6)
        d.line((x, gy0, x, gy1), fill=(24, 30, 42), width=1)

    d.line((gx0, gy0, gx0, gy1), fill=(86, 96, 116), width=3)
    d.line((gx0, gy1, gx1, gy1), fill=(86, 96, 116), width=3)

    # Accent line
    pts = []
    for i in range(7):
        x = gx0 + int((gx1 - gx0) * i / 6)
        y = gy1 - int((gy1 - gy0) * (0.18 + 0.12 * math.sin(i * 0.8) + (i / 6) * 0.55))
        pts.append((x, y))
    d.line(pts, fill=ACCENT, width=5)
    for x, y in pts:
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=INK, outline=ACCENT, width=3)

    # Footer
    d.text((96, h - 110), "Source: link", font=_font(22), fill=MUTED)
    d.text((w - 560, h - 110), "Edition YYYY-MM-DD", font=_font(22), fill=MUTED)

    bg.save(out, "PNG")


def editorial_photo(out: Path):
    # Square for X, also works as IG.
    w = h = 1080
    bg = _radial_gradient(w, h, BG, (16, 36, 46), center=(int(w * 0.3), int(h * 0.25)))
    bg = _add_grain(bg)
    d = ImageDraw.Draw(bg)

    # Photo placeholder frame
    margin = 84
    frame = (margin, 190, w - margin, h - 210)
    d.rounded_rectangle(frame, radius=32, outline=(54, 66, 88), width=2, fill=(14, 18, 26))
    d.text((margin + 36, 210), "EDITORIAL PHOTO", font=_font(26, bold=True), fill=MUTED)
    d.text((margin + 36, 250), "Drop licensed image here", font=_font(22), fill=MUTED)

    # Top brand
    d.text((84, 72), "STEVEN AI DIGEST", font=_font(34, bold=True), fill=INK)

    # Headline
    d.text((84, h - 180), "Headline in two lines max", font=_font(44, bold=True), fill=INK)
    d.text((84, h - 125), "One sentence subhead.", font=_font(26), fill=MUTED)

    # Accent bar
    d.rounded_rectangle((84, h - 58, 280, h - 42), radius=10, fill=ACCENT2)

    bg.save(out, "PNG")


def memo_video_cmd(out_mp4: Path, ffmpeg: Path):
    # 15s, 1080x1080, modern matte gradient, subtle motion.
    # Uses only generated backgrounds + text overlay (no external media).
    out_mp4.parent.mkdir(parents=True, exist_ok=True)

    # Background gradient + slow zoom, then text overlays.
    # We generate background with ffmpeg color sources and blend.
    cmd = (
        f"\"{ffmpeg}\" -y "
        f"-f lavfi -i color=c=#0B0F18:s=1080x1080:d=15:r=30 "
        f"-f lavfi -i color=c=#1B123D:s=1080x1080:d=15:r=30 "
        f"-filter_complex "
        f"[0:v][1:v]blend=all_mode=screen:all_opacity=0.35,"
        f"gblur=sigma=18,"
        f"zoompan=z='min(1.07,1+0.0009*on)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=450:s=1080x1080,"
        f"format=yuv420p,"
        f"drawtext=font='Segoe UI':text='STEVEN AI DIGEST':x=70:y=80:fontsize=52:fontcolor=white@0.95,"
        f"drawtext=font='Segoe UI':text='DAILY MEMO':x=72:y=140:fontsize=26:fontcolor=white@0.55,"
        f"drawtext=font='Segoe UI':text='YOUR HEADLINE HERE':x=70:y=780:fontsize=60:fontcolor=white@0.95,"
        f"drawtext=font='Segoe UI':text='One clean takeaway. No hype.':x=72:y=850:fontsize=30:fontcolor=white@0.62"
        f" "
        f"-c:v libx264 -crf 18 -preset medium -t 15 \"{out_mp4}\""
    )
    return cmd


def main():
    out_dir = ROOT

    chart_slide(out_dir / "A_chart_slide_template.png")
    editorial_photo(out_dir / "B_editorial_photo_template.png")

    ffmpeg = Path(r"C:\Users\Administrator\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe")
    if ffmpeg.exists():
        (out_dir / "C_memo_video_template.cmd").write_text(
            memo_video_cmd(out_dir / "C_memo_video_template.mp4", ffmpeg) + "\n",
            encoding="utf-8",
        )
    else:
        (out_dir / "C_memo_video_template.cmd").write_text(
            "REM ffmpeg not found. Install FFmpeg then re-run generate_templates.py\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
