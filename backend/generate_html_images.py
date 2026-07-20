#!/usr/bin/env python
"""
Régénère les illustrations pédagogiques du chapitre HTML (section 1) avec
le même style graphique que le chapitre CSS (media/courses/css/section2/),
pour une identité visuelle cohérente dans toute l'application.

Écrase les fichiers existants dans media/courses/html/section1/ (mêmes noms
de fichiers déjà référencés dans le contenu des leçons -> aucune migration
de contenu nécessaire).
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
# 1. html-css-js-comparison.png — HTML / CSS / JS, les 3 piliers
# ============================================================
def make_css_js_comparison():
    W, H = 1050, 520
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 32), "Les 3 piliers du développement web", font(23, bold=True), NAVY)

    col_w = 320
    gap = 15
    start_x = (W - (col_w * 3 + gap * 2)) / 2
    top = 78
    col_h = 400

    cols = [
        {
            "title": "HTML", "sub": "Structure",
            "code": ["<h1>Bienvenue</h1>", "<p>Un paragraphe.</p>"],
            "role": "Définit le contenu\net son organisation",
            "analogy": "Les murs et fondations\nd'une maison",
            "line": BLUE_LINE, "fill": BLUE_FILL,
        },
        {
            "title": "CSS", "sub": "Présentation",
            "code": ["h1 {", "  color: blue;", "}"],
            "role": "Stylise l'apparence\nvisuelle",
            "analogy": "La décoration et\nl'aménagement",
            "line": GREEN_LINE, "fill": GREEN_FILL,
        },
        {
            "title": "JavaScript", "sub": "Comportement",
            "code": ["btn.addEventListener(", "  'click', () => {}", ")"],
            "role": "Ajoute de\nl'interactivité",
            "analogy": "L'électricité et\nla domotique",
            "line": ORANGE_LINE, "fill": ORANGE_FILL,
        },
    ]

    f_title = font(21, bold=True)
    f_sub = font(14)
    f_code = font(12, mono=True)
    f_label = font(13, bold=True)
    f_item = font(13)

    for i, col in enumerate(cols):
        x0 = start_x + i * (col_w + gap)
        x1 = x0 + col_w
        y0, y1 = top, top + col_h
        rrect(d, (x0, y0, x1, y1), "#ffffff", col["line"], radius=14, width=2)

        chip_w, chip_h = 130, 30
        cx0 = x0 + (col_w - chip_w) / 2
        rrect(d, (cx0, y0 + 20, cx0 + chip_w, y0 + 20 + chip_h), col["fill"], col["line"], radius=15, width=1)
        text_center(d, (x0 + col_w / 2, y0 + 20 + chip_h / 2 + 1), col["title"], font(15, bold=True), NAVY)

        text_center(d, (x0 + col_w / 2, y0 + 70), col["sub"], f_sub, GRAY)

        code_y0 = y0 + 90
        code_h = 22 * len(col["code"]) + 20
        rrect(d, (x0 + 16, code_y0, x1 - 16, code_y0 + code_h), CODE_BG, CODE_LINE, radius=8, width=1)
        for j, line in enumerate(col["code"]):
            d.text((x0 + 28, code_y0 + 10 + j * 22), line, font=f_code, fill=CODE_TEXT)

        y = code_y0 + code_h + 30
        text_center(d, (x0 + col_w / 2, y), "RÔLE", f_label, col["line"])
        y += 22
        for line in col["role"].split("\n"):
            text_center(d, (x0 + col_w / 2, y), line, f_item, "#1f2937")
            y += 18

        y += 16
        text_center(d, (x0 + col_w / 2, y), "ANALOGIE", f_label, col["line"])
        y += 22
        for line in col["analogy"].split("\n"):
            text_center(d, (x0 + col_w / 2, y), line, f_item, GRAY)
            y += 18

    img.save(os.path.join(OUT_DIR, "html-css-js-comparison.png"))
    print("✅ html-css-js-comparison.png")


# ============================================================
# 2. html-evolution-timeline.png — Timeline HTML 1991 -> aujourd'hui
# ============================================================
def make_evolution_timeline():
    W, H = 1200, 480
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 32), "L'évolution du HTML", font(23, bold=True), NAVY)
    text_center(d, (W / 2, 58), "De 1991 à aujourd'hui", font(14), GRAY)

    milestones = [
        ("1991", "HTML 1.0", "Première version\npar Tim Berners-Lee", BLUE_LINE, BLUE_FILL, True),
        ("1995", "HTML 2.0", "Formulaires,\ntableaux", GREEN_LINE, GREEN_FILL, False),
        ("1997", "HTML 3.2", "Scripts, feuilles\nde style", ORANGE_LINE, ORANGE_FILL, True),
        ("1999", "HTML 4.01", "Séparation\ncontenu/présentation", YELLOW_LINE, YELLOW_FILL, False),
        ("2000", "XHTML 1.0", "Conforme XML,\nplus strict", PURPLE_LINE, PURPLE_FILL, True),
        ("2014", "HTML5", "Vidéo, canvas,\nAPIs modernes", RED_LINE, RED_FILL, False),
        ("Auj.", "Living Standard", "Évolution\ncontinue", BLUE_LINE, BLUE_FILL, True),
    ]

    n = len(milestones)
    margin = 70
    usable_w = W - 2 * margin
    axis_y = H / 2 + 10
    d.line([(margin, axis_y), (W - margin, axis_y)], fill="#cbd5e1", width=3)

    f_year = font(14, bold=True)
    f_name = font(14, bold=True)
    f_desc = font(11)

    for i, (year, name, desc, line, fill, up) in enumerate(milestones):
        x = margin + usable_w * i / (n - 1)
        r = 9
        d.ellipse((x - r, axis_y - r, x + r, axis_y + r), fill=fill, outline=line, width=3)

        box_w, box_h = 140, 100
        if up:
            box_y1 = axis_y - 30
            box_y0 = box_y1 - box_h
            d.line([(x, axis_y - r - 2), (x, box_y1)], fill=line, width=2)
        else:
            box_y0 = axis_y + 30
            box_y1 = box_y0 + box_h
            d.line([(x, axis_y + r + 2), (x, box_y0)], fill=line, width=2)

        box_x0 = max(10, min(W - box_w - 10, x - box_w / 2))
        rrect(d, (box_x0, box_y0, box_x0 + box_w, box_y0 + box_h), "#ffffff", line, radius=10, width=2)

        cx = box_x0 + box_w / 2
        chip_w, chip_h = 60, 22
        rrect(d, (cx - chip_w / 2, box_y0 + 10, cx + chip_w / 2, box_y0 + 10 + chip_h), fill, line, radius=11, width=1)
        text_center(d, (cx, box_y0 + 10 + chip_h / 2 + 1), year, f_year, NAVY)

        text_center(d, (cx, box_y0 + 46), name, f_name, "#1f2937")
        ty = box_y0 + 64
        for dline in desc.split("\n"):
            text_center(d, (cx, ty), dline, f_desc, GRAY)
            ty += 15

    img.save(os.path.join(OUT_DIR, "html-evolution-timeline.png"))
    print("✅ html-evolution-timeline.png")


# ============================================================
# 3. client-server-architecture.png — Cycle client/serveur
# ============================================================
def make_client_server():
    W, H = 980, 280
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 32), "Le cycle de vie d'une page web", font(21, bold=True), NAVY)

    steps = [
        ("Développeur", "Écrit du HTML", BLUE_LINE, BLUE_FILL),
        ("Serveur", "Envoie le HTML", ORANGE_LINE, ORANGE_FILL),
        ("Navigateur", "Parse & construit\nle DOM", GREEN_LINE, GREEN_FILL),
        ("Écran", "Affiche la page", PURPLE_LINE, PURPLE_FILL),
    ]

    n = len(steps)
    box_w, box_h = 190, 130
    gap = (W - n * box_w) / (n + 1)
    y0 = 110
    f_title = font(16, bold=True)
    f_sub = font(12)
    f_arrow = font(22, bold=True)

    for i, (title, sub, line, fill) in enumerate(steps):
        x0 = gap + i * (box_w + gap)
        x1 = x0 + box_w
        rrect(d, (x0, y0, x1, y0 + box_h), fill, line, radius=14, width=2)
        text_center(d, (x0 + box_w / 2, y0 + 45), title, f_title, "#1f2937")
        ty = y0 + 75
        for sline in sub.split("\n"):
            text_center(d, (x0 + box_w / 2, ty), sline, f_sub, GRAY)
            ty += 16

        if i < n - 1:
            ax = x1 + gap / 2
            text_center(d, (ax, y0 + box_h / 2), "→", f_arrow, "#94a3b8")

    img.save(os.path.join(OUT_DIR, "client-server-architecture.png"))
    print("✅ client-server-architecture.png")


# ============================================================
# 4. google-search-anatomy.png — HTML -> résultat Google
# ============================================================
def make_google_anatomy():
    W, H = 900, 480
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 30), "De vos balises HTML au résultat Google", font(20, bold=True), NAVY)

    card_x0, card_y0, card_x1, card_y1 = 260, 80, 780, 230
    rrect(d, (card_x0, card_y0, card_x1, card_y1), "#ffffff", "#e2e8f0", radius=10, width=2)

    f_title = font(17)
    f_url = font(13)
    f_desc = font(13)

    d.text((card_x0 + 20, card_y0 + 20), "Profil de Jean Dupont | Portfolio", font=font(17, bold=True), fill="#1a0dab")
    d.text((card_x0 + 20, card_y0 + 52), "https://monsite.com", font=f_url, fill="#006621")
    desc = "Portfolio personnel de Jean Dupont, développeur web"
    d.text((card_x0 + 20, card_y0 + 80), desc, font=f_desc, fill="#545454")
    desc2 = "passionné par la création de sites modernes..."
    d.text((card_x0 + 20, card_y0 + 102), desc2, font=f_desc, fill="#545454")

    callouts = [
        ("<title>", "Titre cliquable", card_y0 + 28, BLUE_LINE, BLUE_FILL, 11),
        ("URL de la page", "Adresse verte", card_y0 + 60, ORANGE_LINE, ORANGE_FILL, 13),
        ('<meta name="description">', "Texte descriptif", card_y0 + 95, GREEN_LINE, GREEN_FILL, 10),
    ]

    f_label = font(11)

    for tag, label, y, line, fill, tag_size in callouts:
        lx0 = 20
        chip_w = 220
        d.line([(lx0 + chip_w, y), (card_x0 - 10, y)], fill=line, width=2)
        d.ellipse((card_x0 - 14, y - 4, card_x0 - 6, y + 4), fill=line)
        rrect(d, (lx0, y - 16, lx0 + chip_w, y + 16), fill, line, radius=8, width=1)
        text_center(d, (lx0 + chip_w / 2, y - 5), tag, font(tag_size, mono=True, bold=True), "#1f2937")
        text_center(d, (lx0 + chip_w / 2, y + 11), label, f_label, GRAY)

    text_center(
        d, (W / 2, 270),
        "Balises de structure (h1, h2...) → aident au classement",
        font(13), GRAY,
    )

    box2_y0 = 300
    rrect(d, (200, box2_y0, 700, box2_y0 + 60), YELLOW_FILL, YELLOW_LINE, radius=10, width=2)
    text_center(d, (450, box2_y0 + 30), "Un HTML bien structuré améliore votre référencement (SEO)", font(14, bold=True), "#854d0e")

    img.save(os.path.join(OUT_DIR, "google-search-anatomy.png"))
    print("✅ google-search-anatomy.png")


# ============================================================
# 5. html-document-anatomy.png — Anatomie d'un document HTML5
# ============================================================
def make_document_anatomy():
    W, H = 560, 560
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "Anatomie d'un document HTML5", font(19, bold=True), NAVY)

    f_tag = font(13, mono=True, bold=True)
    f_small = font(11, mono=True)

    doctype_w, doctype_h = 220, 30
    dx0 = (W - doctype_w) / 2
    rrect(d, (dx0, 55, dx0 + doctype_w, 55 + doctype_h), "#e2e8f0", "#94a3b8", radius=8, width=1)
    text_center(d, (W / 2, 55 + doctype_h / 2), "<!DOCTYPE html>", f_tag, "#334155")

    outer = [40, 100, W - 40, H - 30]
    rrect(d, tuple(outer), BLUE_FILL, BLUE_LINE, radius=10, width=2)
    text_left(d, (outer[0] + 14, outer[1] + 18), '<html lang="fr">', f_tag, "#1e3a8a")

    head = [outer[0] + 20, outer[1] + 40, outer[2] - 20, outer[1] + 190]
    rrect(d, tuple(head), GREEN_FILL, GREEN_LINE, radius=8, width=2)
    text_left(d, (head[0] + 12, head[1] + 16), "<head> — Métadonnées", font(13, bold=True), "#166534")
    meta_lines = [
        '<meta charset="utf-8">',
        '<meta name="viewport">',
        "<title>Page title</title>",
        '<link rel="stylesheet">',
    ]
    my = head[1] + 40
    for line in meta_lines:
        d.text((head[0] + 16, my), line, font=f_small, fill="#166534")
        my += 24

    body = [outer[0] + 20, head[3] + 16, outer[2] - 20, outer[3] - 16]
    rrect(d, tuple(body), ORANGE_FILL, ORANGE_LINE, radius=8, width=2)
    text_left(d, (body[0] + 12, body[1] + 18), "<body> — Contenu visible", font(13, bold=True), "#9a3412")

    sub_w = body[2] - body[0] - 24
    sub_x0 = body[0] + 12
    header_y = body[1] + 40
    rrect(d, (sub_x0, header_y, sub_x0 + sub_w, header_y + 26), "#ffffff", ORANGE_LINE, radius=6, width=1)
    text_center(d, (sub_x0 + sub_w / 2, header_y + 13), "<header> — Navigation", font(11), "#7c2d12")

    main_y = header_y + 34
    rrect(d, (sub_x0, main_y, sub_x0 + sub_w, main_y + 50), "#ffffff", ORANGE_LINE, radius=6, width=1)
    text_center(d, (sub_x0 + sub_w / 2, main_y + 18), "<main> — Contenu principal", font(11), "#7c2d12")
    text_center(d, (sub_x0 + sub_w / 2, main_y + 36), "<section> • <article>", font(10, mono=True), "#9a3412")

    footer_y = main_y + 58
    rrect(d, (sub_x0, footer_y, sub_x0 + sub_w, footer_y + 26), "#ffffff", ORANGE_LINE, radius=6, width=1)
    text_center(d, (sub_x0 + sub_w / 2, footer_y + 13), "<footer>", font(11), "#7c2d12")

    img.save(os.path.join(OUT_DIR, "html-document-anatomy.png"))
    print("✅ html-document-anatomy.png")


# ============================================================
# 6. html-meta-tags-mindmap.png — Récapitulatif des balises meta
# ============================================================
def make_meta_tags_cheatsheet():
    W, H = 900, 470
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "Les balises meta essentielles", font(21, bold=True), NAVY)

    rows = [
        ("Charset", '<meta charset="UTF-8">', "Supporte tous les caractères (accents, émojis)", BLUE_LINE, BLUE_FILL),
        ("Viewport", '<meta name="viewport" content="width=device-width">', "Adapte la page aux écrans mobiles", GREEN_LINE, GREEN_FILL),
        ("Description", '<meta name="description" content="...">', "Texte affiché sous le titre dans Google", ORANGE_LINE, ORANGE_FILL),
        ("Author", '<meta name="author" content="...">', "Indique l'auteur de la page", YELLOW_LINE, YELLOW_FILL),
        ("Open Graph", '<meta property="og:title" content="...">', "Aperçu personnalisé sur les réseaux sociaux", PURPLE_LINE, PURPLE_FILL),
    ]

    top = 65
    row_h = 74
    col1_x, col2_x = 40, 210
    f_head = font(13, bold=True)
    f_type = font(14, bold=True)
    f_code = font(12, mono=True, bold=True)
    f_desc = font(12)

    text_left(d, (col1_x, top), "BALISE", f_head, GRAY)
    text_left(d, (col2_x, top), "SYNTAXE", f_head, GRAY)
    d.line([(30, top + 18), (W - 30, top + 18)], fill="#cbd5e1", width=2)

    y = top + 32
    for name, code, desc, line, fill in rows:
        rrect(d, (30, y, W - 30, y + row_h - 12), "#ffffff", "#e2e8f0", radius=8, width=1)
        chip_w = 16
        d.rounded_rectangle((40, y + 20, 40 + chip_w, y + 36), radius=4, fill=fill, outline=line, width=1)
        text_left(d, (68, y + 28), name, f_type, "#1f2937")
        text_left(d, (col2_x, y + 20), code, f_code, line)
        text_left(d, (col2_x, y + 42), desc, f_desc, GRAY)
        y += row_h

    img.save(os.path.join(OUT_DIR, "html-meta-tags-mindmap.png"))
    print("✅ html-meta-tags-mindmap.png")


# ============================================================
# 7. viewport-mobile-comparison.png — Avec / sans meta viewport
# ============================================================
def make_viewport_comparison():
    W, H = 900, 550
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 30), "Avec et sans meta viewport, sur mobile", font(21, bold=True), NAVY)

    def phone(cx, top, w, h, title, title_color):
        f_title = font(16, bold=True)
        text_center(d, (cx, top - 22), title, f_title, title_color)
        x0, y0, x1, y1 = cx - w / 2, top, cx + w / 2, top + h
        rrect(d, (x0, y0, x1, y1), "#111827", "#111827", radius=26, width=0)
        sx0, sy0, sx1, sy1 = x0 + 8, y0 + 26, x1 - 8, y1 - 8
        rrect(d, (sx0, sy0, sx1, sy1), "#ffffff", "#111827", radius=4, width=0)
        return sx0, sy0, sx1, sy1

    # Sans viewport : contenu desktop rétréci (texte minuscule, tient plusieurs "colonnes")
    sx0, sy0, sx1, sy1 = phone(W * 0.27, 80, 220, 380, "Sans meta viewport", "#b91c1c")
    tiny = font(5)
    for row in range(14):
        yy = sy0 + 8 + row * 12
        d.line([(sx0 + 4, yy), (sx1 - 4, yy)], fill="#cbd5e1", width=3)
    text_center(d, ((sx0 + sx1) / 2, sy0 + 20), "Page desktop", tiny, "#94a3b8")
    text_center(d, ((sx0 + sx1) / 2, (sy0 + sy1) / 2 + 40), "illisible,\nzoom requis", font(9), "#b91c1c")

    # Avec viewport : contenu adapté, lisible
    sx0b, sy0b, sx1b, sy1b = phone(W * 0.73, 80, 220, 380, "Avec meta viewport", "#15803d")
    pad = 14
    text_center(d, ((sx0b + sx1b) / 2, sy0b + 30), "Mon Site", font(14, bold=True), "#1f2937")
    yy = sy0b + 60
    for row in range(6):
        rrect(d, (sx0b + pad, yy, sx1b - pad, yy + 14), GREEN_FILL, GREEN_LINE, radius=4, width=1)
        yy += 22
    text_center(d, ((sx0b + sx1b) / 2, sy1b - 40), "Contenu\nlisible", font(11, bold=True), "#15803d")

    d.line([(W / 2, 70), (W / 2, 470)], fill="#cbd5e1", width=2)

    box_y = 480
    rrect(d, (150, box_y, W - 150, box_y + 40), YELLOW_FILL, YELLOW_LINE, radius=10, width=2)
    text_center(d, (W / 2, box_y + 20), '<meta name="viewport" content="width=device-width, initial-scale=1.0">', font(12, mono=True, bold=True), "#854d0e")

    img.save(os.path.join(OUT_DIR, "viewport-mobile-comparison.png"))
    print("✅ viewport-mobile-comparison.png")


if __name__ == "__main__":
    make_css_js_comparison()
    make_evolution_timeline()
    make_client_server()
    make_google_anatomy()
    make_document_anatomy()
    make_meta_tags_cheatsheet()
    make_viewport_comparison()
    print("\n✨ 7 illustrations régénérées dans", OUT_DIR)
