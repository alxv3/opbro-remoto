#!/usr/bin/env python3
"""Genera los iconos de la variante Administrador de OPBro Remoto.

Toma el icono base de OPBro (res/icon.png) y le agrega una banda inferior con
el texto ADMIN, en ambar para contrastar con el azul del logo. Los iconos de
la variante Cliente son los originales, sin cambios.

Salidas:
    res/icon-admin.png                                  1024x1024, referencia
    res/icon-admin.ico                                  Explorador (portable)
    flutter/windows/runner/resources/app_icon-admin.ico ventana / barra tareas
    flutter/macos/Runner/AppIcon-admin.icns             Finder / Dock

Uso:
    python3 opbro/gen_icons.py
"""

import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))

BASE_ICON = os.path.join(ROOT, "res", "icon.png")
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

# Banda inferior: empieza a esta fraccion del alto y ocupa el resto.
BAND_TOP = 0.76
# Ambar: contrasta con el azul cielo #38bdf8 del logo.
BAND_COLOR = (245, 158, 11, 255)
TEXT_COLOR = (255, 255, 255, 255)
# Debajo de este tamano el texto no se lee, se deja solo la banda de color.
MIN_TEXT_SIZE = 64

OUT_PNG = os.path.join(ROOT, "res", "icon-admin.png")
OUT_ICO = os.path.join(ROOT, "res", "icon-admin.ico")
OUT_WIN_ICO = os.path.join(
    ROOT, "flutter", "windows", "runner", "resources", "app_icon-admin.ico"
)
OUT_ICNS = os.path.join(ROOT, "flutter", "macos", "Runner", "AppIcon-admin.icns")

ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)

ICNS_SPECS = (
    ("16x16", 16),
    ("16x16@2x", 32),
    ("32x32", 32),
    ("32x32@2x", 64),
    ("128x128", 128),
    ("128x128@2x", 256),
    ("256x256", 256),
    ("256x256@2x", 512),
    ("512x512", 512),
    ("512x512@2x", 1024),
)


def render(size: int, base: Image.Image) -> Image.Image:
    """Icono de `size` px con el logo arriba y la banda ADMIN abajo."""
    band_y = int(size * BAND_TOP)
    margin_top = max(1, int(size * 0.03))
    available = band_y - margin_top
    # El logo no debe tocarse con la banda.
    side = max(1, int(available * 0.95))
    logo = base.resize((side, side), Image.LANCZOS)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    # alpha_composite y no paste(..., mask): paste aplicaria la mascara dos
    # veces y al cuadrar la alfa deja el relleno del logo transparentado.
    canvas.alpha_composite(logo, ((size - side) // 2, margin_top))

    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, band_y, size - 1, size - 1), fill=BAND_COLOR)

    if size >= MIN_TEXT_SIZE:
        band_h = size - band_y
        font = ImageFont.truetype(FONT_PATH, max(8, int(band_h * 0.62)))
        text = "ADMIN"
        box = draw.textbbox((0, 0), text, font=font)
        tw = box[2] - box[0]
        th = box[3] - box[1]
        x = (size - tw) // 2 - box[0]
        # Centrado opticalo: el texto se apoya un poco sobre la linea media
        # para que las mayusculas no queden flojas dentro de la banda.
        y = band_y + (band_h - th) // 2 - box[1] - max(1, int(size * 0.01))
        draw.text((x, y), text, font=font, fill=TEXT_COLOR)

    return canvas


def write_ico(img: Image.Image, path: str) -> None:
    img.save(path, format="ICO", sizes=[(s, s) for s in ICO_SIZES])


def write_icns(path: str, base: Image.Image) -> None:
    iconset = tempfile.mkdtemp(suffix=".iconset")
    try:
        for name, px in ICNS_SPECS:
            render(px, base).save(os.path.join(iconset, f"icon_{name}.png"))
        subprocess.run(
            ["iconutil", "-c", "icns", iconset, "-o", path], check=True
        )
    finally:
        shutil.rmtree(iconset, ignore_errors=True)


def main() -> int:
    if not os.path.exists(FONT_PATH):
        print(f"ERROR: no existe la fuente {FONT_PATH}", flush=True)
        return 1

    base = Image.open(BASE_ICON).convert("RGBA")
    master = render(1024, base)

    master.save(OUT_PNG)
    write_ico(master, OUT_ICO)
    write_ico(master, OUT_WIN_ICO)
    write_icns(OUT_ICNS, base)

    for p in (OUT_PNG, OUT_ICO, OUT_WIN_ICO, OUT_ICNS):
        print(f"escrito {p} ({os.path.getsize(p)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
