"""Attach real, license-clear edition thumbnails from Wikimedia Commons.

- Downloads source images from upload.wikimedia.org
- Creates web-optimized thumbnails in assets/visuals/editions/<date>/thumb.webp
- Writes a small credit.json per edition with attribution + license URL

This avoids placeholder template visuals while staying within free/open licensing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "visuals" / "editions"


@dataclass
class Source:
    url: str
    author: str
    title: str
    license_name: str
    license_url: str
    source_page: str


# Curated Commons sources (open licensed). Keep this list tight and high-signal.
SOURCES: dict[str, Source] = {
    # Data center racks photo
    "datacenter_racks": Source(
        url="https://upload.wikimedia.org/wikipedia/commons/b/b3/Datacenter_Server_Racks_%2822370909788%29.jpg",
        title="Datacenter Server Racks (22370909788)",
        author="Tony Webster",
        license_name="CC BY 2.0",
        license_url="https://creativecommons.org/licenses/by/2.0/",
        source_page="https://commons.wikimedia.org/wiki/File:Datacenter_Server_Racks_(22370909788).jpg",
    ),
    # GPU card photo
    "geforce_210": Source(
        url="https://upload.wikimedia.org/wikipedia/commons/3/38/ASUS_NVIDIA_GeForce_210_silent_graphics_card_with_HDMI.JPG",
        title="ASUS NVIDIA GeForce 210 silent graphics card with HDMI",
        author="Joydeep (JDP90)",
        license_name="CC BY-SA 3.0",
        license_url="https://creativecommons.org/licenses/by-sa/3.0/",
        source_page="https://commons.wikimedia.org/wiki/File:ASUS_NVIDIA_GeForce_210_silent_graphics_card_with_HDMI.JPG",
    ),
}

# Map edition dates to a chosen source.
EDITION_SOURCE = {
    "2026-02-04": "geforce_210",
    "2025-12-05": "datacenter_racks",
    "2025-11-18": "geforce_210",
    "2025-10-06": "datacenter_racks",
    "2025-09-15": "datacenter_racks",
    "2025-08-07": "geforce_210",
}


def download(url: str) -> bytes:
    headers = {
        "User-Agent": "StevenAiDigest/1.0 (contact: stevenaidigest.netlify.app)"
    }
    r = requests.get(url, headers=headers, timeout=60)
    r.raise_for_status()
    return r.content


def make_thumb(src_bytes: bytes, out_path: Path, size=(1280, 720)):
    img = Image.open(BytesIO(src_bytes)).convert("RGB")

    # center-crop to target aspect
    tw, th = size
    target_ratio = tw / th
    w, h = img.size
    src_ratio = w / h

    if src_ratio > target_ratio:
        # crop width
        new_w = int(h * target_ratio)
        x0 = (w - new_w) // 2
        img = img.crop((x0, 0, x0 + new_w, h))
    else:
        # crop height
        new_h = int(w / target_ratio)
        y0 = (h - new_h) // 2
        img = img.crop((0, y0, w, y0 + new_h))

    img = img.resize((tw, th), Image.Resampling.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "WEBP", quality=88, method=6)


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    for date, source_key in EDITION_SOURCE.items():
        src = SOURCES[source_key]
        out_dir = OUT / date
        thumb = out_dir / "thumb.webp"
        credit = out_dir / "credit.json"

        raw = download(src.url)
        make_thumb(raw, thumb)

        credit_data = {
            "title": src.title,
            "author": src.author,
            "license": src.license_name,
            "licenseUrl": src.license_url,
            "sourcePage": src.source_page,
            "sourceFile": src.url,
            "notes": "Cropped/resized for web."
        }
        credit.write_text(json.dumps(credit_data, indent=2), encoding="utf-8")

        print(f"{date}: wrote {thumb.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
