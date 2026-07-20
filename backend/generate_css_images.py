#!/usr/bin/env python
"""
Génère les illustrations pédagogiques pour le chapitre CSS (section 2).
Style cohérent avec les illustrations HTML existantes (media/courses/html/section1/).
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
CODE_BG, CODE_LINE = "#1e293b", "#334155"
CODE_TEXT = "#e2e8f0"


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
# 1. css-rule-anatomy.png — Anatomie d'une règle CSS
# ============================================================
def make_rule_anatomy():
    W, H = 800, 380
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 30), "Anatomie d'une règle CSS", font(22, bold=True), NAVY)

    # Code line pieces
    y_code = 130
    f_code = font(26, mono=True, bold=True)
    parts = [
        ("h1", BLUE_LINE),
        (" { ", GRAY),
        ("color", GREEN_LINE),
        (": ", GRAY),
        ("blue", ORANGE_LINE),
        ("; ", GRAY),
        ("}", GRAY),
    ]
    # compute total width to center
    total_w = sum(d.textbbox((0, 0), t, font=f_code)[2] for t, _ in parts)
    x = (W - total_w) / 2
    positions = []
    for t, color in parts:
        bbox = d.textbbox((0, 0), t, font=f_code)
        w = bbox[2] - bbox[0]
        d.text((x, y_code - 15), t, font=f_code, fill=color)
        positions.append((t, color, x, x + w))
        x += w

    # Labels with connector lines
    label_f = font(15, bold=True)
    small_f = font(13)

    def label_below(idx, label, sub, color):
        t, c, x0, x1 = positions[idx]
        cx = (x0 + x1) / 2
        ly = 230
        d.line([(cx, y_code + 20), (cx, ly - 10)], fill=color, width=2)
        text_center(d, (cx, ly), label, label_f, color)
        text_center(d, (cx, ly + 20), sub, small_f, GRAY)

    label_below(0, "Sélecteur", "quel élément ?", BLUE_LINE)
    label_below(2, "Propriété", "quoi changer ?", GREEN_LINE)
    label_below(4, "Valeur", "avec quoi ?", ORANGE_LINE)

    # Bloc de déclarations bracket note
    y2 = 300
    text_center(d, (W / 2, y2), "{ propriété: valeur; }  →  bloc de déclarations", font(15), NAVY)
    text_center(d, (W / 2, y2 + 30), "⚠ chaque déclaration se termine par un point-virgule  ;", font(14), RED_LINE)

    img.save(os.path.join(OUT_DIR, "css-rule-anatomy.png"))
    print("✅ css-rule-anatomy.png")


# ============================================================
# 2. css-application-methods.png — 3 façons d'appliquer du CSS
# ============================================================
def make_application_methods():
    W, H = 1050, 560
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 32), "Les 3 façons d'appliquer du CSS", font(24, bold=True), NAVY)

    col_w = 320
    gap = 15
    start_x = (W - (col_w * 3 + gap * 2)) / 2
    top = 80
    col_h = 450

    cols = [
        {
            "title": "CSS en ligne",
            "sub": "attribut style",
            "code": ['<h1 style="', '  color:blue;">', "Titre</h1>"],
            "pros": [],
            "cons": ["Mélange contenu/style", "Non réutilisable", "Priorité difficile\nà surcharger"],
            "line": RED_LINE, "fill": RED_FILL, "recommended": False,
        },
        {
            "title": "CSS interne",
            "sub": "balise <style>",
            "code": ["<style>", "  h1 { color: blue; }", "</style>"],
            "pros": ["Pratique 1 page"],
            "cons": ["Non réutilisable", "Alourdit le HTML"],
            "line": YELLOW_LINE, "fill": YELLOW_FILL, "recommended": False,
        },
        {
            "title": "CSS externe",
            "sub": "fichier .css lié",
            "code": ['<link rel="stylesheet"', '  href="style.css">'],
            "pros": ["Réutilisable", "Mis en cache", "Facile à maintenir"],
            "cons": [],
            "line": GREEN_LINE, "fill": GREEN_FILL, "recommended": True,
        },
    ]

    f_title = font(19, bold=True)
    f_sub = font(13)
    f_code = font(13, mono=True)
    f_item = font(13)
    f_badge = font(12, bold=True)

    for i, col in enumerate(cols):
        x0 = start_x + i * (col_w + gap)
        x1 = x0 + col_w
        y0 = top
        y1 = top + col_h
        rrect(d, (x0, y0, x1, y1), "#ffffff", col["line"], radius=14, width=3 if col["recommended"] else 2)

        if col["recommended"]:
            badge_w, badge_h = 130, 26
            bx0 = x1 - badge_w - 12
            by0 = y0 - 13
            rrect(d, (bx0, by0, bx0 + badge_w, by0 + badge_h), GREEN_LINE, GREEN_LINE, radius=13, width=1)
            text_center(d, (bx0 + badge_w / 2, by0 + badge_h / 2 + 1), "✔ RECOMMANDÉ", f_badge, "#ffffff")

        text_center(d, (x0 + col_w / 2, y0 + 40), col["title"], f_title, NAVY)
        text_center(d, (x0 + col_w / 2, y0 + 64), col["sub"], f_sub, GRAY)

        code_y0 = y0 + 85
        code_h = 26 * len(col["code"]) + 20
        rrect(d, (x0 + 16, code_y0, x1 - 16, code_y0 + code_h), CODE_BG, CODE_LINE, radius=8, width=1)
        for j, line in enumerate(col["code"]):
            d.text((x0 + 28, code_y0 + 12 + j * 26), line, font=f_code, fill=CODE_TEXT)

        item_y = code_y0 + code_h + 24
        for pro in col["pros"]:
            for k, sub_line in enumerate(pro.split("\n")):
                prefix = "✓ " if k == 0 else "   "
                d.text((x0 + 24, item_y), prefix + sub_line, font=f_item, fill="#15803d")
                item_y += 20
            item_y += 4
        for con in col["cons"]:
            for k, sub_line in enumerate(con.split("\n")):
                prefix = "✗ " if k == 0 else "   "
                d.text((x0 + 24, item_y), prefix + sub_line, font=f_item, fill="#b91c1c")
                item_y += 20
            item_y += 4

    img.save(os.path.join(OUT_DIR, "css-application-methods.png"))
    print("✅ css-application-methods.png")


# ============================================================
# 3. css-box-model.png — Box model imbriqué (convention DevTools)
# ============================================================
def make_box_model():
    W, H = 560, 560
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 30), "Le Box Model CSS", font(22, bold=True), NAVY)

    layers = [
        ("margin", ORANGE_FILL, ORANGE_LINE, 70),
        ("border", YELLOW_FILL, YELLOW_LINE, 55),
        ("padding", GREEN_FILL, GREEN_LINE, 40),
    ]

    top = 65
    box = [30, top, W - 30, H - 30]
    f_label = font(15, bold=True)
    f_small = font(12)

    for name, fill, line, inset in layers:
        rrect(d, tuple(box), fill, line, radius=10, width=2)
        text_left(d, (box[0] + 14, box[1] + 18), name, f_label, "#1f2937")
        box = [box[0] + inset, box[1] + inset, box[2] - inset, box[3] - inset]

    # content box (innermost)
    rrect(d, tuple(box), BLUE_FILL, BLUE_LINE, radius=8, width=2)
    cx = (box[0] + box[2]) / 2
    cy = (box[1] + box[3]) / 2
    text_center(d, (cx, cy - 12), "content", font(16, bold=True), "#1e3a8a")
    text_center(d, (cx, cy + 12), "width × height", f_small, "#1e3a8a")

    img.save(os.path.join(OUT_DIR, "css-box-model.png"))
    print("✅ css-box-model.png")


# ============================================================
# 4. css-box-sizing-comparison.png — content-box vs border-box
# ============================================================
def make_box_sizing_comparison():
    W, H = 900, 480
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 30), "content-box vs border-box", font(22, bold=True), NAVY)

    def panel(x_center, title, title_color, width_label, box_px, total_label, formula):
        f_title = font(17, bold=True)
        f_code = font(13, mono=True)
        f_small = font(13)

        text_center(d, (x_center, 68), title, f_title, title_color)

        half = box_px / 2
        outer = [x_center - half - 24, 100, x_center + half + 24, 100 + box_px + 48]
        rrect(d, tuple(outer), ORANGE_FILL, ORANGE_LINE, radius=8, width=2)
        text_left(d, (outer[0] + 10, outer[1] + 14), "border", font(11, bold=True), "#9a3412")

        inner = [outer[0] + 16, outer[1] + 26, outer[2] - 16, outer[3] - 16]
        rrect(d, tuple(inner), BLUE_FILL, BLUE_LINE, radius=6, width=2)
        text_center(d, ((inner[0] + inner[2]) / 2, (inner[1] + inner[3]) / 2), width_label, f_code, "#1e3a8a")

        y_note = outer[3] + 30
        text_center(d, (x_center, y_note), formula, f_small, GRAY)
        text_center(d, (x_center, y_note + 24), total_label, font(15, bold=True), title_color)

    panel(
        W * 0.27, "content-box (défaut)", "#c2410c",
        "width: 200px", 200,
        "Largeur totale = 250px",
        "200 + padding(20×2) + border(5×2)",
    )
    panel(
        W * 0.73, "box-sizing: border-box", "#15803d",
        "width: 200px", 160,
        "Largeur totale = 200px",
        "padding et border inclus dans les 200px",
    )

    d.line([(W / 2, 90), (W / 2, H - 60)], fill="#cbd5e1", width=2)

    img.save(os.path.join(OUT_DIR, "css-box-sizing-comparison.png"))
    print("✅ css-box-sizing-comparison.png")


# ============================================================
# 5. css-selectors-cheatsheet.png — Récapitulatif des sélecteurs
# ============================================================
def make_selectors_cheatsheet():
    W, H = 860, 470
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "Sélecteurs CSS — Récapitulatif", font(21, bold=True), NAVY)

    rows = [
        ("Élément", "p { }", "Tous les <p>", BLUE_LINE, BLUE_FILL),
        ("Classe", ".alerte { }", "Éléments avec class=\"alerte\"", GREEN_LINE, GREEN_FILL),
        ("ID", "#titre { }", "L'élément avec id=\"titre\" (unique)", ORANGE_LINE, ORANGE_FILL),
        ("Descendant", "nav a { }", "Tous les <a> dans <nav>", YELLOW_LINE, YELLOW_FILL),
        ("Enfant direct", "ul > li { }", "Les <li> enfants directs de <ul>", BLUE_LINE, BLUE_FILL),
        ("Pseudo-classe", "a:hover { }", "Un <a> survolé par la souris", GREEN_LINE, GREEN_FILL),
    ]

    top = 65
    row_h = 62
    col1_x, col2_x, col3_x = 40, 260, 470
    f_head = font(14, bold=True)
    f_type = font(15, bold=True)
    f_code = font(15, mono=True, bold=True)
    f_desc = font(13)

    text_left(d, (col1_x, top), "TYPE", f_head, GRAY)
    text_left(d, (col2_x, top), "SYNTAXE", f_head, GRAY)
    text_left(d, (col3_x, top), "CIBLE", f_head, GRAY)
    d.line([(30, top + 18), (W - 30, top + 18)], fill="#cbd5e1", width=2)

    y = top + 34
    for name, code, desc, line, fill in rows:
        rrect(d, (30, y, W - 30, y + row_h - 12), "#ffffff", "#e2e8f0", radius=8, width=1)
        chip_w = 16
        d.rounded_rectangle((40, y + (row_h - 12) / 2 - 8, 40 + chip_w, y + (row_h - 12) / 2 + 8), radius=4, fill=fill, outline=line, width=1)
        text_left(d, (68, y + (row_h - 12) / 2), name, f_type, "#1f2937")
        text_left(d, (col2_x, y + (row_h - 12) / 2), code, f_code, line)
        text_left(d, (col3_x, y + (row_h - 12) / 2), desc, f_desc, GRAY)
        y += row_h

    img.save(os.path.join(OUT_DIR, "css-selectors-cheatsheet.png"))
    print("✅ css-selectors-cheatsheet.png")


if __name__ == "__main__":
    make_rule_anatomy()
    make_application_methods()
    make_box_model()
    make_box_sizing_comparison()
    make_selectors_cheatsheet()
    print("\n✨ 5 illustrations générées dans", OUT_DIR)
