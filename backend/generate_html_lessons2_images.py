#!/usr/bin/env python
"""
Illustrations pour les 6 nouvelles leçons du chapitre HTML (texte, listes,
liens/images, sémantique, tableaux, formulaires). Même style graphique que
generate_html_images.py / generate_css_images.py.
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = "media/courses/html/section1"
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
PURPLE_FILL, PURPLE_LINE = "#f3e8ff", "#a855f7"
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
# 1. html-heading-hierarchy.png — Hiérarchie des titres h1-h6
# ============================================================
def make_heading_hierarchy():
    W, H = 760, 480
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 30), "La hiérarchie des titres", font(21, bold=True), NAVY)

    levels = [
        ("h1", "Titre principal de la page", 30, BLUE_LINE),
        ("h2", "Un grand titre de section", 25, GREEN_LINE),
        ("h3", "Un sous-titre", 21, ORANGE_LINE),
        ("h4", "Encore un niveau", 18, YELLOW_LINE),
        ("h5", "Presque le plus petit", 15, PURPLE_LINE),
        ("h6", "Le plus petit niveau", 13, RED_LINE),
    ]

    top = 65
    row_h = 65
    tag_x = 60
    for i, (tag, sample, size, color) in enumerate(levels):
        y = top + i * row_h
        chip_w, chip_h = 56, 30
        rrect(d, (tag_x, y, tag_x + chip_w, y + chip_h), BG, color, radius=8, width=2)
        text_center(d, (tag_x + chip_w / 2, y + chip_h / 2 + 1), f"<{tag}>", font(13, mono=True, bold=True), color)

        text_left(d, (tag_x + chip_w + 24, y + chip_h / 2 + 1), sample, font(size, bold=True), "#1f2937")

        d.line([(tag_x + chip_w + 20, y + chip_h - 6), (W - 40, y + chip_h - 6)], fill="#e2e8f0", width=1)

    text_center(d, (W / 2, top + 6 * row_h + 15), "La taille diminue, mais le SENS (l'ordre) reste ce qui compte vraiment", font(13), GRAY)

    img.save(os.path.join(OUT_DIR, "html-heading-hierarchy.png"))
    print("✅ html-heading-hierarchy.png")


# ============================================================
# 2. html-lists-comparison.png — <ul> vs <ol>
# ============================================================
def make_lists_comparison():
    W, H = 820, 420
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 30), "Liste à puces vs liste numérotée", font(21, bold=True), NAVY)

    def panel(x0, title, tag, color, fill, items, numbered):
        x1 = x0 + 340
        y0, y1 = 75, 360
        rrect(d, (x0, y0, x1, y1), "#ffffff", color, radius=14, width=2)

        chip_w = 90
        rrect(d, (x0 + 20, y0 + 20, x0 + 20 + chip_w, y0 + 50), fill, color, radius=8, width=1)
        text_center(d, (x0 + 20 + chip_w / 2, y0 + 35), tag, font(14, mono=True, bold=True), NAVY)

        text_left(d, (x0 + 130, y0 + 35), title, font(15, bold=True), "#1f2937")

        iy = y0 + 90
        for idx, item in enumerate(items):
            marker = f"{idx + 1}." if numbered else "•"
            marker_color = color
            d.text((x0 + 40, iy), marker, font=font(16, bold=True), fill=marker_color)
            d.text((x0 + 70, iy), item, font=font(15), fill="#1f2937")
            iy += 42

    panel(40, "Liste à puces", "<ul>", GREEN_LINE, GREEN_FILL,
          ["Pommes", "Lait", "Pain"], numbered=False)
    panel(430, "Liste numérotée", "<ol>", BLUE_LINE, BLUE_FILL,
          ["Préchauffer le four", "Mélanger les ingrédients", "Enfourner 25 minutes"], numbered=True)

    text_center(d, (250, 385), "L'ordre n'a pas d'importance", font(12), GRAY)
    text_center(d, (640, 385), "L'ordre est essentiel", font(12), GRAY)

    img.save(os.path.join(OUT_DIR, "html-lists-comparison.png"))
    print("✅ html-lists-comparison.png")


# ============================================================
# 3. html-link-image-anatomy.png — Anatomie de <a> et <img>
# ============================================================
def make_link_image_anatomy():
    W, H = 820, 480
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "Anatomie d'un lien et d'une image", font(20, bold=True), NAVY)

    def code_row(y, parts, label_y):
        f_code = font(15, mono=True, bold=True)
        total_w = sum(d.textbbox((0, 0), t, font=f_code)[2] for t, _ in parts)
        x = (W - total_w) / 2
        positions = []
        for t, color in parts:
            bbox = d.textbbox((0, 0), t, font=f_code)
            w = bbox[2] - bbox[0]
            d.text((x, y - 12), t, font=f_code, fill=color)
            positions.append((x, x + w, color))
            x += w
        return positions

    # --- Lien ---
    text_left(d, (60, 70), "Le lien :", font(14, bold=True), GRAY)
    parts_a = [
        ("<a ", GRAY), ("href", BLUE_LINE), ("=\"url\" ", GRAY),
        ("target", GREEN_LINE), ("=\"_blank\"", GRAY), (">", GRAY),
        ("Texte", ORANGE_LINE), ("</a>", GRAY),
    ]
    y1 = 100
    positions1 = code_row(y1, parts_a, y1 + 30)

    def label_under(positions, idx, text, color, y_line_end):
        x0, x1, _ = positions[idx]
        cx = (x0 + x1) / 2
        d.line([(cx, y1 + 12), (cx, y_line_end - 8)], fill=color, width=2)
        text_center(d, (cx, y_line_end + 8), text, font(11, bold=True), color)

    label_under(positions1, 1, "destination", BLUE_LINE, 150)
    label_under(positions1, 3, "nouvel onglet\n(+ rel=\"noopener\")", GREEN_LINE, 150)
    label_under(positions1, 6, "texte cliquable", ORANGE_LINE, 150)

    d.line([(60, 210), (W - 60, 210)], fill="#e2e8f0", width=1)

    # --- Image ---
    text_left(d, (60, 250), "L'image :", font(14, bold=True), GRAY)
    parts_img = [
        ("<img ", GRAY), ("src", BLUE_LINE), ("=\"photo.jpg\" ", GRAY),
        ("alt", GREEN_LINE), ("=\"...\"", GRAY), (">", GRAY),
    ]
    y2 = 285
    positions2 = code_row(y2, parts_img, y2 + 30)

    def label_under2(positions, idx, text, color, y_line_end):
        x0, x1, _ = positions[idx]
        cx = (x0 + x1) / 2
        d.line([(cx, y2 + 12), (cx, y_line_end - 8)], fill=color, width=2)
        text_center(d, (cx, y_line_end + 8), text, font(11, bold=True), color)

    label_under2(positions2, 1, "fichier source", BLUE_LINE, 335)
    label_under2(positions2, 3, "texte alternatif\n(accessibilité + SEO)", GREEN_LINE, 335)

    box_y = 400
    rrect(d, (100, box_y, W - 100, box_y + 50), YELLOW_FILL, YELLOW_LINE, radius=10, width=2)
    text_center(d, (W / 2, box_y + 25), "⚠️ <img> n'a pas de balise fermante, </img> n'existe pas", font(13, bold=True), "#854d0e")

    img.save(os.path.join(OUT_DIR, "html-link-image-anatomy.png"))
    print("✅ html-link-image-anatomy.png")


# ============================================================
# 4. html-semantic-page-layout.png — Plan sémantique d'une page
# ============================================================
def make_semantic_page_layout():
    W, H = 640, 620
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "Plan sémantique d'une page HTML5", font(19, bold=True), NAVY)

    outer = [40, 60, W - 40, H - 30]
    rrect(d, tuple(outer), "#ffffff", "#cbd5e1", radius=10, width=2)

    # header
    header = [outer[0] + 16, outer[1] + 16, outer[2] - 16, outer[1] + 110]
    rrect(d, tuple(header), BLUE_FILL, BLUE_LINE, radius=8, width=2)
    text_left(d, (header[0] + 14, header[1] + 20), "<header>", font(13, mono=True, bold=True), "#1e3a8a")
    nav = [header[0] + 16, header[1] + 44, header[2] - 16, header[3] - 14]
    rrect(d, tuple(nav), "#ffffff", BLUE_LINE, radius=6, width=1)
    text_center(d, ((nav[0] + nav[2]) / 2, (nav[1] + nav[3]) / 2), "<nav>", font(12, mono=True, bold=True), "#1e3a8a")

    # main
    main = [outer[0] + 16, header[3] + 16, outer[2] - 16, outer[3] - 90]
    rrect(d, tuple(main), GREEN_FILL, GREEN_LINE, radius=8, width=2)
    text_left(d, (main[0] + 14, main[1] + 20), "<main>", font(13, mono=True, bold=True), "#166534")

    article = [main[0] + 16, main[1] + 44, main[0] + (main[2] - main[0]) * 0.62, main[3] - 14]
    rrect(d, tuple(article), "#ffffff", GREEN_LINE, radius=6, width=1)
    text_center(d, ((article[0] + article[2]) / 2, (article[1] + article[3]) / 2 - 10), "<article>", font(12, mono=True, bold=True), "#166534")
    text_center(d, ((article[0] + article[2]) / 2, (article[1] + article[3]) / 2 + 12), "contenu principal", font(10), "#166534")

    aside = [article[2] + 12, main[1] + 44, main[2] - 14, main[3] - 14]
    rrect(d, tuple(aside), "#ffffff", GREEN_LINE, radius=6, width=1)
    text_center(d, ((aside[0] + aside[2]) / 2, (aside[1] + aside[3]) / 2 - 10), "<aside>", font(12, mono=True, bold=True), "#166534")
    text_center(d, ((aside[0] + aside[2]) / 2, (aside[1] + aside[3]) / 2 + 12), "contenu lié", font(10), "#166534")

    # footer
    footer = [outer[0] + 16, main[3] + 16, outer[2] - 16, outer[3] - 16]
    rrect(d, tuple(footer), ORANGE_FILL, ORANGE_LINE, radius=8, width=2)
    text_center(d, ((footer[0] + footer[2]) / 2, (footer[1] + footer[3]) / 2), "<footer>", font(13, mono=True, bold=True), "#9a3412")

    img.save(os.path.join(OUT_DIR, "html-semantic-page-layout.png"))
    print("✅ html-semantic-page-layout.png")


# ============================================================
# 5. html-table-anatomy.png — Anatomie d'un tableau
# ============================================================
def make_table_anatomy():
    W, H = 620, 400
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "Anatomie d'un tableau HTML", font(19, bold=True), NAVY)

    row_h = 68
    outer = [60, 65, W - 60, 65 + 40 + row_h * 3 + 24]
    rrect(d, tuple(outer), BLUE_FILL, BLUE_LINE, radius=10, width=2)
    text_left(d, (outer[0] + 12, outer[1] + 16), "<table>", font(12, mono=True, bold=True), "#1e3a8a")

    col_w = (outer[2] - outer[0] - 32) / 2

    def cell_row(y0, row_fill, row_line, row_label, row_label_color, cell_label, cell_label_color, texts, text_font, text_color, cell_fill="#ffffff", cell_line="#cbd5e1"):
        rrect(d, (outer[0] + 16, y0, outer[2] - 16, y0 + row_h), row_fill, row_line, radius=6, width=1)
        text_left(d, (outer[0] + 24, y0 + 16), row_label, font(11, mono=True, bold=True), row_label_color)

        c1 = [outer[0] + 24, y0 + 30, outer[0] + 16 + col_w - 8, y0 + row_h - 10]
        c2 = [outer[0] + 24 + col_w, y0 + 30, outer[2] - 24, y0 + row_h - 10]
        for box, label in [(c1, texts[0]), (c2, texts[1])]:
            rrect(d, tuple(box), cell_fill, cell_line, radius=5, width=1)
            text_center(d, ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), label, text_font, text_color)
        text_center(d, ((c1[0] + c1[2]) / 2, c1[1] - 12), cell_label, font(9, mono=True), cell_label_color)
        text_center(d, ((c2[0] + c2[2]) / 2, c2[1] - 12), cell_label, font(9, mono=True), cell_label_color)

    y = outer[1] + 40
    cell_row(y, GREEN_FILL, GREEN_LINE, "<tr>", "#166534", "<th>", "#9a3412",
              ["Produit", "Prix"], font(12, bold=True), "#9a3412", cell_line=ORANGE_LINE)

    y += row_h + 12
    cell_row(y, YELLOW_FILL, YELLOW_LINE, "<tr>", "#854d0e", "<td>", "#475569",
              ["Clavier", "29,99 €"], font(12), "#334155")

    y += row_h + 12
    cell_row(y, YELLOW_FILL, YELLOW_LINE, "<tr>", "#854d0e", "<td>", "#475569",
              ["Souris", "14,99 €"], font(12), "#334155")

    img.save(os.path.join(OUT_DIR, "html-table-anatomy.png"))
    print("✅ html-table-anatomy.png")


# ============================================================
# 6. html-form-label-anatomy.png — label for / input id
# ============================================================
def make_form_label_anatomy():
    W, H = 700, 430
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "Associer un label à son champ", font(20, bold=True), NAVY)

    f_code = font(16, mono=True, bold=True)
    left_margin = 110

    def code_line(y, parts):
        x = left_margin
        value_box = None
        for t, color in parts:
            bbox = d.textbbox((0, 0), t, font=f_code)
            w = bbox[2] - bbox[0]
            d.text((x, y - 12), t, font=f_code, fill=color)
            if color == RED_LINE:
                value_box = (x, x + w)
            x += w
        return value_box

    y1 = 100
    for_box = code_line(y1, [
        ("<label ", GRAY), ("for", ORANGE_LINE), ("=\"nom\"", RED_LINE), (">Votre nom :</label>", GRAY),
    ])

    y2 = 170
    id_box = code_line(y2, [
        ("<input ", GRAY), ("id", ORANGE_LINE), ("=\"nom\"", RED_LINE), (" type=\"text\">", GRAY),
    ])

    # Highlight both matching values and connect them on the right-hand side,
    # away from the code text, so nothing overlaps.
    rrect(d, (for_box[0] - 4, y1 + 4, for_box[1] + 4, y1 + 24), RED_FILL, RED_LINE, radius=4, width=2)
    rrect(d, (id_box[0] - 4, y2 + 4, id_box[1] + 4, y2 + 24), RED_FILL, RED_LINE, radius=4, width=2)

    rail_x = max(for_box[1], id_box[1]) + 40
    y1_mid = y1 + 14
    y2_mid = y2 + 14
    d.line([(for_box[1] + 4, y1_mid), (rail_x, y1_mid)], fill=RED_LINE, width=2)
    d.line([(id_box[1] + 4, y2_mid), (rail_x, y2_mid)], fill=RED_LINE, width=2)
    d.line([(rail_x, y1_mid), (rail_x, y2_mid)], fill=RED_LINE, width=2)
    text_left(d, (rail_x + 14, (y1_mid + y2_mid) / 2), "identiques !", font(13, bold=True), "#b91c1c")

    box_y = 260
    rrect(d, (70, box_y, W - 70, box_y + 90), GREEN_FILL, GREEN_LINE, radius=10, width=2)
    text_center(d, (W / 2, box_y + 30), "✓ Cliquer sur le texte du label active le champ", font(13, bold=True), "#166534")
    text_center(d, (W / 2, box_y + 60), "✓ Un lecteur d'écran annonce le label au focus", font(13, bold=True), "#166534")

    img.save(os.path.join(OUT_DIR, "html-form-label-anatomy.png"))
    print("✅ html-form-label-anatomy.png")


if __name__ == "__main__":
    make_heading_hierarchy()
    make_lists_comparison()
    make_link_image_anatomy()
    make_semantic_page_layout()
    make_table_anatomy()
    make_form_label_anatomy()
    print("\n✨ 6 illustrations générées dans", OUT_DIR)
