#!/usr/bin/env python
"""
Illustrations pour les 6 nouvelles leçons du chapitre CSS (couleurs,
typographie, unités, display, bordures/ombres, pseudo-classes). Même style
graphique que generate_css_images.py.
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = "media/courses/css/section2"
os.makedirs(OUT_DIR, exist_ok=True)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(size, bold=False, mono=False):
    if mono:
        name = "DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf"
    else:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


NAVY = "#1a2b4c"
GRAY = "#475569"
BG = "#f8f9fb"

BLUE_FILL, BLUE_LINE = "#dbeafe", "#3b82f6"
GREEN_FILL, GREEN_LINE = "#dcfce7", "#22c55e"
ORANGE_FILL, ORANGE_LINE = "#ffedd5", "#f97316"
YELLOW_FILL, YELLOW_LINE = "#fef9c3", "#eab308"
RED_FILL, RED_LINE = "#fee2e2", "#ef4444"
CODE_BG, CODE_LINE, CODE_TEXT = "#1e293b", "#334155", "#e2e8f0"


def text_center(draw, xy, txt, f, fill):
    x, y = xy
    bbox = draw.textbbox((0, 0), txt, font=f)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x - w / 2, y - h / 2 - bbox[1]), txt, font=f, fill=fill)


def text_left(draw, xy, txt, f, fill):
    x, y = xy
    bbox = draw.textbbox((0, 0), txt, font=f)
    h = bbox[3] - bbox[1]
    draw.text((x, y - h / 2 - bbox[1]), txt, font=f, fill=fill)


def rrect(draw, box, fill, outline, radius=10, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


# ============================================================
# 1. css-color-formats.png — 4 façons d'écrire la même couleur
# ============================================================
def make_color_formats():
    W, H = 900, 460
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "4 façons d'écrire la même couleur", font(20, bold=True), NAVY)

    RED = "#ef4444"
    formats = [
        ("Mot-clé", "red"),
        ("Hexadécimal", "#ef4444"),
        ("RGB", "rgb(239, 68, 68)"),
        ("HSL", "hsl(0, 84%, 60%)"),
    ]

    col_w, gap = 195, 15
    start_x = (W - (col_w * 4 + gap * 3)) / 2
    top = 70

    for i, (label, code) in enumerate(formats):
        x0 = start_x + i * (col_w + gap)
        x1 = x0 + col_w
        rrect(d, (x0, top, x1, top + 230), "#ffffff", "#e2e8f0", radius=12, width=2)
        text_center(d, ((x0 + x1) / 2, top + 28), label, font(14, bold=True), NAVY)

        swatch = [x0 + 20, top + 50, x1 - 20, top + 150]
        rrect(d, tuple(swatch), RED, RED, radius=10, width=0)

        code_y = top + 175
        rrect(d, (x0 + 12, code_y, x1 - 12, code_y + 38), CODE_BG, CODE_LINE, radius=6, width=1)
        text_center(d, ((x0 + x1) / 2, code_y + 19), code, font(11, mono=True, bold=True), CODE_TEXT)

    box_y = 330
    rrect(d, (150, box_y, W - 150, box_y + 100), "#ffffff", "#e2e8f0", radius=12, width=2)
    text_center(d, (W / 2, box_y + 26), "Avec transparence : rgba() / hsla()", font(13, bold=True), NAVY)

    # transparency demo: colored bg with a semi-transparent overlay swatch
    demo_bg = [190, box_y + 44, 350, box_y + 84]
    rrect(d, tuple(demo_bg), "#fbbf24", "#fbbf24", radius=8, width=0)
    overlay = Image.new("RGBA", (120, 40), (0, 0, 0, 130))
    img.paste(Image.alpha_composite(img.crop((200, box_y + 44, 320, box_y + 84)).convert("RGBA"), overlay), (200, box_y + 44))
    text_left(d, (370, box_y + 64), "rgba(0, 0, 0, 0.5) posé sur un fond", font(12), GRAY)

    img.save(os.path.join(OUT_DIR, "css-color-formats.png"))
    print("✅ css-color-formats.png")


# ============================================================
# 2. css-line-height-comparison.png
# ============================================================
def make_line_height_comparison():
    W, H = 820, 420
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "L'impact de line-height sur la lisibilité", font(19, bold=True), NAVY)

    def panel(x0, title, color_line, color_fill, line_height_px, label):
        x1 = x0 + 340
        y0, y1 = 70, 370
        rrect(d, (x0, y0, x1, y1), "#ffffff", color_line, radius=12, width=2)
        text_center(d, ((x0 + x1) / 2, y0 + 30), title, font(15, bold=True), NAVY)

        chip_w = 170
        rrect(d, (x0 + (340 - chip_w) / 2, y0 + 48, x0 + (340 - chip_w) / 2 + chip_w, y0 + 76), color_fill, color_line, radius=6, width=1)
        text_center(d, ((x0 + x1) / 2, y0 + 62), label, font(12, mono=True, bold=True), NAVY)

        # simulated text lines
        ty = y0 + 100
        widths = [280, 260, 300, 240, 270, 220]
        for w in widths:
            d.rounded_rectangle((x0 + 20, ty, x0 + 20 + w, ty + 12), radius=4, fill="#cbd5e1")
            ty += line_height_px

    panel(50, "line-height: 1.0", RED_LINE, RED_FILL, 20, "line-height: 1.0")
    panel(430, "line-height: 1.6", GREEN_LINE, GREEN_FILL, 34, "line-height: 1.6")

    text_center(d, (220, 385), "Lignes serrées, fatigant à lire", font(12), GRAY)
    text_center(d, (600, 385), "Bien aéré, confortable", font(12), GRAY)

    img.save(os.path.join(OUT_DIR, "css-line-height-comparison.png"))
    print("✅ css-line-height-comparison.png")


# ============================================================
# 3. css-units-comparison.png — em (cascade) vs rem (stable)
# ============================================================
def make_units_comparison():
    W, H = 900, 480
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "em (s'accumule) vs rem (toujours stable)", font(19, bold=True), NAVY)

    # --- em panel: nested boxes ---
    x0 = 50
    text_center(d, (x0 + 190, 65), "em — relatif au parent", font(14, bold=True), RED_LINE)

    box1 = [x0, 85, x0 + 380, 440]
    rrect(d, tuple(box1), "#ffffff", "#e2e8f0", radius=10, width=2)
    text_left(d, (box1[0] + 14, box1[1] + 20), "html { font-size: 16px; }", font(10, mono=True), GRAY)

    box2 = [box1[0] + 20, box1[1] + 40, box1[2] - 20, box1[3] - 20]
    rrect(d, tuple(box2), RED_FILL, RED_LINE, radius=8, width=2)
    text_left(d, (box2[0] + 12, box2[1] + 18), ".a { font-size: 1.5em; } → 24px", font(10, mono=True, bold=True), "#991b1b")

    box3 = [box2[0] + 20, box2[1] + 36, box2[2] - 20, box2[3] - 20]
    rrect(d, tuple(box3), "#fecaca", RED_LINE, radius=8, width=2)
    text_left(d, (box3[0] + 12, box3[1] + 18), ".b { font-size: 1.5em; } → 36px", font(10, mono=True, bold=True), "#991b1b")

    box4 = [box3[0] + 20, box3[1] + 36, box3[2] - 20, box3[3] - 20]
    rrect(d, tuple(box4), "#fca5a5", RED_LINE, radius=8, width=2)
    text_center(d, ((box4[0] + box4[2]) / 2, (box4[1] + box4[3]) / 2), "54px !", font(13, bold=True), "#7f1d1d")

    # --- rem panel: flat boxes, all same reference ---
    x1 = 470
    text_center(d, (x1 + 190, 65), "rem — toujours relatif à <html>", font(14, bold=True), GREEN_LINE)

    boxr = [x1, 85, x1 + 380, 440]
    rrect(d, tuple(boxr), "#ffffff", "#e2e8f0", radius=10, width=2)
    text_left(d, (boxr[0] + 14, boxr[1] + 20), "html { font-size: 16px; }", font(10, mono=True), GRAY)

    labels = [
        (".a { font-size: 1.5rem; } → 24px", 24),
        (".b { font-size: 1.5rem; } → 24px", 24),
        (".c { font-size: 1.5rem; } → 24px", 24),
    ]
    ry = boxr[1] + 55
    for label, _ in labels:
        rrect(d, (boxr[0] + 20, ry, boxr[2] - 20, ry + 90), GREEN_FILL, GREEN_LINE, radius=8, width=2)
        text_center(d, ((boxr[0] + boxr[2]) / 2, ry + 45), label, font(11, mono=True, bold=True), "#166534")
        ry += 105

    img.save(os.path.join(OUT_DIR, "css-units-comparison.png"))
    print("✅ css-units-comparison.png")


# ============================================================
# 4. css-display-comparison.png — block / inline / inline-block
# ============================================================
def make_display_comparison():
    W, H = 780, 610
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "block, inline et inline-block", font(20, bold=True), NAVY)

    # block
    y0 = 60
    rrect(d, (40, y0, W - 40, y0 + 230), "#ffffff", "#e2e8f0", radius=12, width=2)
    text_left(d, (56, y0 + 22), "display: block  →  toute la largeur, chacun sur sa ligne", font(13, bold=True), NAVY)
    by = y0 + 45
    for i in range(3):
        rrect(d, (56, by, W - 56, by + 50), BLUE_FILL, BLUE_LINE, radius=6, width=2)
        text_center(d, (W / 2, by + 25), f"<div> {i + 1}", font(11, bold=True), "#1e3a8a")
        by += 58

    # inline
    y1 = y0 + 250
    rrect(d, (40, y1, W - 40, y1 + 90), "#ffffff", "#e2e8f0", radius=12, width=2)
    text_left(d, (56, y1 + 22), "display: inline  →  largeur du contenu, reste sur la ligne", font(13, bold=True), NAVY)
    bx = 56
    for i in range(3):
        w = 90
        rrect(d, (bx, y1 + 42, bx + w, y1 + 72), GREEN_FILL, GREEN_LINE, radius=14, width=2)
        text_center(d, (bx + w / 2, y1 + 57), f"<span> {i + 1}", font(10, bold=True), "#166534")
        bx += w + 8

    # inline-block
    y2 = y1 + 110
    rrect(d, (40, y2, W - 40, y2 + 130), "#ffffff", "#e2e8f0", radius=12, width=2)
    text_left(d, (56, y2 + 22), "display: inline-block  →  reste sur la ligne ET accepte width/height", font(13, bold=True), NAVY)
    bx = 56
    for i in range(3):
        w = 190
        rrect(d, (bx, y2 + 45, bx + w, y2 + 95), ORANGE_FILL, ORANGE_LINE, radius=8, width=2)
        text_center(d, (bx + w / 2, y2 + 70), f"<a> {i + 1} (width fixe)", font(10, bold=True), "#9a3412")
        bx += w + 12

    img.save(os.path.join(OUT_DIR, "css-display-comparison.png"))
    print("✅ css-display-comparison.png")


# ============================================================
# 5. css-border-radius-shadow.png
# ============================================================
def make_border_radius_shadow():
    W, H = 860, 420
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "border-radius et box-shadow", font(20, bold=True), NAVY)

    text_left(d, (60, 65), "border-radius :", font(13, bold=True), GRAY)
    radii = [("0", 0), ("8px", 8), ("24px", 24), ("50%", 45)]
    bx = 220
    for label, r in radii:
        rrect(d, (bx, 55, bx + 90, 55 + 90), BLUE_FILL, BLUE_LINE, radius=r, width=2)
        text_center(d, (bx + 45, 160), label, font(11, mono=True, bold=True), "#1e3a8a")
        bx += 130

    d.line([(40, 190), (W - 40, 190)], fill="#e2e8f0", width=1)

    text_left(d, (60, 225), "box-shadow :", font(13, bold=True), GRAY)

    def shadow_card(x0, blur, label):
        y0 = 250
        w, h = 200, 110
        # draw fake shadow as blurred-looking rectangle via multiple offset rects
        for i in range(blur, 0, -2):
            alpha_color = "#e2e8f0"
            d.rounded_rectangle((x0 + i * 0.4, y0 + i * 0.6, x0 + w + i * 0.4, y0 + h + i * 0.6), radius=10, fill=alpha_color)
        rrect(d, (x0, y0, x0 + w, y0 + h), "#ffffff", "#e2e8f0", radius=10, width=2)
        text_center(d, (x0 + w / 2, y0 + h / 2), label, font(11, mono=True, bold=True), NAVY)

    shadow_card(70, 6, "box-shadow léger")
    shadow_card(330, 22, "box-shadow marqué")
    shadow_card(590, 0, "sans ombre")

    img.save(os.path.join(OUT_DIR, "css-border-radius-shadow.png"))
    print("✅ css-border-radius-shadow.png")


# ============================================================
# 6. css-pseudo-states.png — normal / hover / active
# ============================================================
def make_pseudo_states():
    W, H = 820, 380
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "Un bouton dans ses différents états", font(20, bold=True), NAVY)

    states = [
        ("Normal", "#2563eb", "#1d4ed8", 1.0, "aucune pseudo-classe"),
        (":hover", "#1e40af", "#1e3a8a", 1.0, "souris au-dessus"),
        (":active", "#1e3a8a", "#172554", 0.96, "pendant le clic"),
    ]

    col_w = 230
    gap = 30
    start_x = (W - (col_w * 3 + gap * 2)) / 2
    top = 80

    for i, (label, color, shadow_color, scale, desc) in enumerate(states):
        x0 = start_x + i * (col_w + gap)
        rrect(d, (x0, top, x0 + col_w, top + 220), "#ffffff", "#e2e8f0", radius=12, width=2)
        text_center(d, (x0 + col_w / 2, top + 26), label, font(14, mono=True, bold=True), NAVY)

        bw, bh = int(150 * scale), int(52 * scale)
        bx0 = x0 + (col_w - bw) / 2
        by0 = top + 70
        rrect(d, (bx0, by0, bx0 + bw, by0 + bh), color, color, radius=10, width=0)
        text_center(d, (bx0 + bw / 2, by0 + bh / 2), "Bouton", font(13, bold=True), "#ffffff")

        text_center(d, (x0 + col_w / 2, top + 165), desc, font(11), GRAY)

    d.line([(start_x + col_w + gap / 2, top + 40), (start_x + col_w + gap / 2, top + 200)], fill="#cbd5e1", width=1)
    d.line([(start_x + 2 * col_w + gap + gap / 2, top + 40), (start_x + 2 * col_w + gap + gap / 2, top + 200)], fill="#cbd5e1", width=1)

    box_y = 320
    rrect(d, (100, box_y, W - 100, box_y + 45), YELLOW_FILL, YELLOW_LINE, radius=10, width=2)
    text_center(d, (W / 2, box_y + 22), "transition: background-color 0.3s ease; → passage en douceur entre ces états", font(12, bold=True), "#854d0e")

    img.save(os.path.join(OUT_DIR, "css-pseudo-states.png"))
    print("✅ css-pseudo-states.png")


if __name__ == "__main__":
    make_color_formats()
    make_line_height_comparison()
    make_units_comparison()
    make_display_comparison()
    make_border_radius_shadow()
    make_pseudo_states()
    print("\n✨ 6 illustrations générées dans", OUT_DIR)
