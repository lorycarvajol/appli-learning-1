"""
Illustrations du chapitre 2 — CSS.

Meme fusion que pour le chapitre HTML : les 5 figures d'origine et
les 6 ajoutees ensuite partagent un dossier de sortie.

Regenere par `python manage.py generate_course_images`.
Les PNG produits sont versionnes : cette commande ne sert qu'a les
retoucher, jamais a amorcer un environnement.
"""
import os

from PIL import Image, ImageDraw

from .palette import (
    BG, BLUE_FILL, BLUE_LINE, CODE_BG, CODE_LINE, CODE_TEXT, GRAY, GREEN_FILL,
    GREEN_LINE, NAVY, ORANGE_FILL, ORANGE_LINE, PURPLE_FILL, PURPLE_LINE,
    RED_FILL, RED_LINE, YELLOW_FILL, YELLOW_LINE,
    ensure_dir, font, rrect, text_center, text_left,
)
from . import palette


OUT_DIR = palette.SECTION_2_CSS


# --- issu de generate_css_images.py ---
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

# --- issu de generate_css_lessons2_images.py ---
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


def build():
    """Dessine toutes les figures de ce chapitre. Ecrase les fichiers."""
    ensure_dir(OUT_DIR)
    make_rule_anatomy()
    make_application_methods()
    make_box_model()
    make_box_sizing_comparison()
    make_selectors_cheatsheet()
    make_color_formats()
    make_line_height_comparison()
    make_units_comparison()
    make_display_comparison()
    make_border_radius_shadow()
    make_pseudo_states()
    return 11
