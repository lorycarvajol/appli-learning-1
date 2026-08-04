"""
Illustrations du chapitre 3 — JavaScript.

Les 7 figures du chapitre JavaScript.

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


OUT_DIR = palette.SECTION_3_JS


# --- issu de generate_js_images.py ---
# ============================================================
# 1. js-variables-types.png
# ============================================================
def make_variables_types():
    W, H = 820, 420
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "Variables : des boîtes étiquetées", font(20, bold=True), NAVY)

    vars_ = [
        ("const prenom", '"Alex"', "string", BLUE_FILL, BLUE_LINE, "fixe"),
        ("const age", "25", "number", GREEN_FILL, GREEN_LINE, "fixe"),
        ("let score", "0", "number", ORANGE_FILL, ORANGE_LINE, "modifiable"),
        ("const estActif", "true", "boolean", PURPLE_FILL, PURPLE_LINE, "fixe"),
    ]

    col_w, gap = 175, 15
    start_x = (W - (col_w * 4 + gap * 3)) / 2
    top = 70

    for i, (name, value, typ, fill, line, lock) in enumerate(vars_):
        x0 = start_x + i * (col_w + gap)
        x1 = x0 + col_w
        rrect(d, (x0, top, x1, top + 230), "#ffffff", line, radius=12, width=2)

        text_center(d, ((x0 + x1) / 2, top + 28), name, font(11, mono=True, bold=True), NAVY)

        box = [x0 + 20, top + 55, x1 - 20, top + 140]
        rrect(d, tuple(box), fill, line, radius=8, width=2)
        text_center(d, ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), value, font(15, mono=True, bold=True), NAVY)

        chip_w = 90
        rrect(d, (x0 + (col_w - chip_w) / 2, top + 160, x0 + (col_w - chip_w) / 2 + chip_w, top + 186), CODE_BG, CODE_LINE, radius=12, width=1)
        text_center(d, (x0 + col_w / 2, top + 173), typ, font(10, mono=True), CODE_TEXT)

        lock_color = "#166534" if lock == "fixe" else "#9a3412"
        text_center(d, (x0 + col_w / 2, top + 210), lock, font(12, bold=True), lock_color)

    text_center(d, (W / 2, 335), "const : ne peut plus changer      let : peut être réassignée", font(13, bold=True), GRAY)

    box_y = 360
    rrect(d, (140, box_y, W - 140, box_y + 42), YELLOW_FILL, YELLOW_LINE, radius=10, width=2)
    text_center(d, (W / 2, box_y + 21), "typeof renvoie le type sous forme de texte : \"string\", \"number\", \"boolean\"", font(12, bold=True), "#854d0e")

    img.save(os.path.join(OUT_DIR, "js-variables-types.png"))
    print("✅ js-variables-types.png")


# ============================================================
# 2. js-conditions-flowchart.png
# ============================================================
def make_conditions_flowchart():
    W, H = 640, 560
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "if / else if / else en cascade", font(19, bold=True), NAVY)

    start = [220, 55, 420, 95]
    rrect(d, tuple(start), CODE_BG, CODE_LINE, radius=20, width=1)
    text_center(d, ((start[0] + start[2]) / 2, (start[1] + start[3]) / 2), "note = 14", font(13, mono=True, bold=True), CODE_TEXT)

    steps = [
        ("note >= 16 ?", "Très bien", RED_LINE, RED_FILL, False),
        ("note >= 12 ?", "Bien", ORANGE_LINE, ORANGE_FILL, True),
        ("note >= 10 ?", "Passable", YELLOW_LINE, YELLOW_FILL, False),
        ("sinon", "Insuffisant", GREEN_LINE, GREEN_FILL, False),
    ]

    y = 115
    for cond, result, line, fill, is_match in steps:
        diamond_cy = y + 30
        rrect(d, (170, y, 470, y + 60), "#ffffff", "#cbd5e1" if not is_match else line, radius=10, width=3 if is_match else 2)
        text_center(d, (320, diamond_cy), cond, font(13, mono=True, bold=True), NAVY)

        # arrow to result box (right side) if match
        result_box = [500, y, 620, y + 60]
        if is_match:
            rrect(d, tuple(result_box), fill, line, radius=10, width=3)
            text_center(d, ((result_box[0] + result_box[2]) / 2, (result_box[1] + result_box[3]) / 2), f'"{result}"', font(12, bold=True), NAVY)
            d.line([(470, diamond_cy), (500, diamond_cy)], fill=line, width=3)
            text_left(d, (475, diamond_cy - 14), "oui", font(10, bold=True), line)
        else:
            text_center(d, ((result_box[0] + result_box[2]) / 2, (result_box[1] + result_box[3]) / 2), f'"{result}"', font(11), "#cbd5e1")

        if y + 60 < 115 + 60 * 3:
            d.line([(320, y + 60), (320, y + 78)], fill="#cbd5e1", width=2)
            text_left(d, (326, y + 69), "non", font(10, bold=True), GRAY)
        y += 78

    box_y = 490
    rrect(d, (60, box_y, W - 60, box_y + 45), BLUE_FILL, BLUE_LINE, radius=10, width=2)
    text_center(d, (W / 2, box_y + 22), "Dès qu'une condition est vraie, les suivantes sont ignorées", font(12, bold=True), "#1e3a8a")

    img.save(os.path.join(OUT_DIR, "js-conditions-flowchart.png"))
    print("✅ js-conditions-flowchart.png")


# ============================================================
# 3. js-boucles-anatomy.png
# ============================================================
def make_boucles_anatomy():
    W, H = 780, 470
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "Anatomie d'une boucle for", font(20, bold=True), NAVY)

    f_code = font(17, mono=True, bold=True)
    parts = [
        ("for (", GRAY), ("let i = 0", BLUE_LINE), ("; ", GRAY),
        ("i < 5", GREEN_LINE), ("; ", GRAY), ("i++", ORANGE_LINE), (") { ... }", GRAY),
    ]
    total_w = sum(d.textbbox((0, 0), t, font=f_code)[2] for t, _ in parts)
    x = (W - total_w) / 2
    y = 100
    positions = []
    for t, color in parts:
        bbox = d.textbbox((0, 0), t, font=f_code)
        w = bbox[2] - bbox[0]
        d.text((x, y - 13), t, font=f_code, fill=color)
        positions.append((x, x + w, color))
        x += w

    labels = [
        (1, "Initialisation", "exécutée 1 seule fois", BLUE_LINE, 150),
        (3, "Condition", "vérifiée avant\nchaque tour", GREEN_LINE, 210),
        (5, "Incrémentation", "exécutée après\nchaque tour", ORANGE_LINE, 270),
    ]
    for idx, title, sub, color, shelf_y in labels:
        x0, x1, _ = positions[idx]
        cx = (x0 + x1) / 2
        d.line([(cx, y + 12), (cx, shelf_y - 10), (100, shelf_y - 10), (100, shelf_y)], fill=color, width=2)
        text_left(d, (60, shelf_y + 2), title, font(13, bold=True), color)
        sub_y = shelf_y + 20
        for sub_line in sub.split("\n"):
            text_left(d, (60, sub_y), sub_line, font(10), GRAY)
            sub_y += 14

    # cycle diagram
    cy_y = 370
    rrect(d, (250, cy_y, 530, cy_y + 90), "#ffffff", "#e2e8f0", radius=12, width=2)
    text_center(d, (390, cy_y + 25), "0 → 1 → 2 → 3 → 4", font(15, mono=True, bold=True), NAVY)
    text_center(d, (390, cy_y + 55), "puis i < 5 devient faux : la boucle s'arrête", font(12), GRAY)

    img.save(os.path.join(OUT_DIR, "js-boucles-anatomy.png"))
    print("✅ js-boucles-anatomy.png")


# ============================================================
# 4. js-fonctions-anatomy.png
# ============================================================
def make_fonctions_anatomy():
    W, H = 700, 420
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "Une fonction : entrée → traitement → sortie", font(18, bold=True), NAVY)

    f_code = font(15, mono=True, bold=True)
    parts = [
        ("function ", GRAY), ("addition", NAVY), ("(", GRAY),
        ("a, b", BLUE_LINE), (") { ", GRAY), ("return a + b;", GREEN_LINE), (" }", GRAY),
    ]
    total_w = sum(d.textbbox((0, 0), t, font=f_code)[2] for t, _ in parts)
    x = (W - total_w) / 2
    y = 80
    positions = []
    for t, color in parts:
        bbox = d.textbbox((0, 0), t, font=f_code)
        w = bbox[2] - bbox[0]
        d.text((x, y - 11), t, font=f_code, fill=color)
        positions.append((x, x + w))
        x += w

    x0, x1 = positions[3]
    cx = (x0 + x1) / 2
    d.line([(cx, y + 10), (cx, 120)], fill=BLUE_LINE, width=2)
    text_center(d, (cx, 138), "paramètres", font(12, bold=True), BLUE_LINE)

    x0, x1 = positions[5]
    cx = (x0 + x1) / 2
    d.line([(cx, y + 10), (cx, 120)], fill=GREEN_LINE, width=2)
    text_center(d, (cx, 138), "valeur renvoyée", font(12, bold=True), GREEN_LINE)

    # machine diagram
    my = 190
    in_box = [60, my, 200, my + 70]
    rrect(d, tuple(in_box), BLUE_FILL, BLUE_LINE, radius=10, width=2)
    text_center(d, ((in_box[0] + in_box[2]) / 2, (in_box[1] + in_box[3]) / 2), "a = 2\nb = 3", font(13, mono=True, bold=True), "#1e3a8a")

    mid_box = [280, my - 15, 460, my + 85]
    rrect(d, tuple(mid_box), CODE_BG, CODE_LINE, radius=10, width=2)
    text_center(d, ((mid_box[0] + mid_box[2]) / 2, (mid_box[1] + mid_box[3]) / 2), "addition(a, b)", font(13, mono=True, bold=True), CODE_TEXT)

    out_box = [540, my, 640, my + 70]
    rrect(d, tuple(out_box), GREEN_FILL, GREEN_LINE, radius=10, width=2)
    text_center(d, ((out_box[0] + out_box[2]) / 2, (out_box[1] + out_box[3]) / 2), "5", font(20, mono=True, bold=True), "#166534")

    ay = my + 35
    d.line([(200, ay), (280, ay)], fill=GRAY, width=2)
    d.line([(460, ay), (540, ay)], fill=GRAY, width=2)

    box_y = 320
    rrect(d, (80, box_y, W - 80, box_y + 60), YELLOW_FILL, YELLOW_LINE, radius=10, width=2)
    text_center(d, (W / 2, box_y + 22), "console.log() affiche une valeur", font(12, bold=True), "#854d0e")
    text_center(d, (W / 2, box_y + 42), "return la renvoie pour être réutilisée ailleurs dans le programme", font(12, bold=True), "#854d0e")

    img.save(os.path.join(OUT_DIR, "js-fonctions-anatomy.png"))
    print("✅ js-fonctions-anatomy.png")


# ============================================================
# 5. js-tableaux-index.png
# ============================================================
def make_tableaux_index():
    W, H = 900, 360
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "Un tableau, indexé à partir de 0", font(20, bold=True), NAVY)

    text_left(d, (60, 70), 'const fruits = ["Pomme", "Banane", "Orange"];', font(13, mono=True, bold=True), NAVY)

    items = ["Pomme", "Banane", "Orange"]
    colors = [(BLUE_FILL, BLUE_LINE), (GREEN_FILL, GREEN_LINE), (ORANGE_FILL, ORANGE_LINE)]
    box_w = 180
    gap = 20
    total_slots = 4  # 3 éléments existants + 1 case fantôme pour push()
    start_x = (W - (box_w * total_slots + gap * (total_slots - 1))) / 2
    top = 110

    for i, (item, (fill, line)) in enumerate(zip(items, colors)):
        x0 = start_x + i * (box_w + gap)
        x1 = x0 + box_w
        rrect(d, (x0, top, x1, top + 90), fill, line, radius=10, width=2)
        text_center(d, ((x0 + x1) / 2, top + 45), item, font(15, bold=True), NAVY)

        chip_w = 50
        rrect(d, (x0 + (box_w - chip_w) / 2, top + 100, x0 + (box_w - chip_w) / 2 + chip_w, top + 130), CODE_BG, CODE_LINE, radius=8, width=1)
        text_center(d, (x0 + box_w / 2, top + 115), f"[{i}]", font(13, mono=True, bold=True), CODE_TEXT)

    push_x0 = start_x + 3 * (box_w + gap)
    rrect(d, (push_x0, top, push_x0 + box_w, top + 90), "#f1f5f9", "#94a3b8", radius=10, width=2)
    text_center(d, (push_x0 + box_w / 2, top + 35), "?", font(20, bold=True), "#94a3b8")
    text_center(d, (push_x0 + box_w / 2, top + 65), "push(...)", font(11, mono=True), "#64748b")

    text_center(d, (W / 2, 265), "fruits[0] → \"Pomme\"     fruits.length → 3", font(14, mono=True, bold=True), GRAY)

    box_y = 300
    rrect(d, (100, box_y, W - 100, box_y + 45), RED_FILL, RED_LINE, radius=10, width=2)
    text_center(d, (W / 2, box_y + 22), "⚠ Le premier élément est fruits[0], pas fruits[1] !", font(13, bold=True), "#991b1b")

    img.save(os.path.join(OUT_DIR, "js-tableaux-index.png"))
    print("✅ js-tableaux-index.png")


# ============================================================
# 6. js-dom-tree.png
# ============================================================
def make_dom_tree():
    W, H = 640, 480
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "Le DOM : votre HTML, sous forme d'arbre", font(17, bold=True), NAVY)

    def node(cx, cy, label, fill, line, w=130, h=40, mono=True):
        box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
        rrect(d, tuple(box), fill, line, radius=8, width=2)
        text_center(d, (cx, cy), label, font(11, mono=mono, bold=True), NAVY)
        return box

    html_box = node(W / 2, 65, "<html>", "#ffffff", "#cbd5e1")
    body_box = node(W / 2, 130, "<body>", "#ffffff", "#cbd5e1")
    d.line([(W / 2, 85), (W / 2, 110)], fill="#cbd5e1", width=2)

    h1_box = node(W * 0.28, 200, "<h1>", BLUE_FILL, BLUE_LINE)
    p_box = node(W * 0.5, 200, "<p class=\"msg\">", GREEN_FILL, GREEN_LINE, w=160)
    btn_box = node(W * 0.76, 200, "<button>", ORANGE_FILL, ORANGE_LINE)

    for bx in (h1_box, p_box, btn_box):
        cx2 = (bx[0] + bx[2]) / 2
        d.line([(W / 2, 150), (cx2, 180)], fill="#cbd5e1", width=2)

    # querySelector arrow pointing at .msg
    arrow_y = 260
    text_center(d, (W * 0.5, arrow_y), "document.querySelector('.msg')", font(11, mono=True, bold=True), GREEN_LINE)
    d.line([(W * 0.5, 220), (W * 0.5, arrow_y - 12)], fill=GREEN_LINE, width=2)

    box_y = 300
    rrect(d, (60, box_y, W - 60, box_y + 130), GREEN_FILL, GREEN_LINE, radius=12, width=2)
    text_center(d, (W / 2, box_y + 26), "Une fois sélectionné :", font(13, bold=True), "#166534")
    text_left(d, (90, box_y + 55), "élément.textContent = \"Nouveau texte\";", font(12, mono=True), "#166534")
    text_left(d, (90, box_y + 80), "élément.classList.add('visible');", font(12, mono=True), "#166534")
    text_left(d, (90, box_y + 105), "élément.style.color = 'blue';", font(12, mono=True), "#166534")

    img.save(os.path.join(OUT_DIR, "js-dom-tree.png"))
    print("✅ js-dom-tree.png")


# ============================================================
# 7. js-evenements-flow.png
# ============================================================
def make_evenements_flow():
    W, H = 860, 320
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_center(d, (W / 2, 28), "Le cycle d'un événement", font(20, bold=True), NAVY)

    steps = [
        ("1", "L'utilisateur\nclique", BLUE_FILL, BLUE_LINE),
        ("2", "L'événement\n'click' se déclenche", ORANGE_FILL, ORANGE_LINE),
        ("3", "Le callback\ns'exécute", GREEN_FILL, GREEN_LINE),
        ("4", "Le DOM\nest mis à jour", PURPLE_FILL, PURPLE_LINE),
    ]

    box_w = 170
    gap = 40
    start_x = (W - (box_w * 4 + gap * 3)) / 2
    top = 80

    for i, (icon, label, fill, line) in enumerate(steps):
        x0 = start_x + i * (box_w + gap)
        x1 = x0 + box_w
        rrect(d, (x0, top, x1, top + 140), fill, line, radius=14, width=2)
        badge_r = 20
        badge_cx = (x0 + x1) / 2
        badge_cy = top + 38
        d.ellipse((badge_cx - badge_r, badge_cy - badge_r, badge_cx + badge_r, badge_cy + badge_r), fill="#ffffff", outline=line, width=2)
        text_center(d, (badge_cx, badge_cy), icon, font(18, bold=True), line)
        ty = top + 85
        for line_txt in label.split("\n"):
            text_center(d, ((x0 + x1) / 2, ty), line_txt, font(12, bold=True), NAVY)
            ty += 18

        if i < 3:
            arrow_x = x1 + gap / 2
            text_center(d, (arrow_x, top + 70), "→", font(24, bold=True), "#94a3b8")

    code_y = 250
    rrect(d, (150, code_y, W - 150, code_y + 45), CODE_BG, CODE_LINE, radius=10, width=1)
    text_center(d, (W / 2, code_y + 22), "bouton.addEventListener('click', () => { ... });", font(12, mono=True, bold=True), CODE_TEXT)

    img.save(os.path.join(OUT_DIR, "js-evenements-flow.png"))
    print("✅ js-evenements-flow.png")


def build():
    """Dessine toutes les figures de ce chapitre. Ecrase les fichiers."""
    ensure_dir(OUT_DIR)
    make_variables_types()
    make_conditions_flowchart()
    make_boucles_anatomy()
    make_fonctions_anatomy()
    make_tableaux_index()
    make_dom_tree()
    make_evenements_flow()
    return 7
