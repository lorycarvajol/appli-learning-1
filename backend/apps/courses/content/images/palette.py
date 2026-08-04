"""
Socle graphique commun des illustrations de cours.

Les cinq générateurs (`generate_html_images.py`, `generate_css_images.py`, …)
redéfinissaient chacun la même palette et les mêmes quatre primitives de dessin.
Les fonctions étaient identiques au caractère près ; les palettes, elles, avaient
commencé à diverger — deux fichiers avaient perdu `PURPLE`, trois écrivaient les
couleurs de code sur une ligne, deux sur trois. Une identité visuelle qui dépend
de cinq copies synchronisées à la main ne le reste pas longtemps.

Tout est ici. Les modules de section n'écrivent plus que leurs figures.

⚠️ Rendu **serveur** : il faut Pillow et les polices DejaVu (paquet Debian
`fonts-dejavu-core`), tous deux installés par le Dockerfile du backend. Rien de
tout cela n'est nécessaire en production — les PNG sont versionnés — mais la
commande `generate_course_images` en a besoin pour les régénérer.
"""
import os

from PIL import ImageFont

# Racine des illustrations, relative à BASE_DIR (`backend/`).
MEDIA_ROOT = 'media/courses'

SECTION_1_HTML = f'{MEDIA_ROOT}/html/section1'
SECTION_2_CSS = f'{MEDIA_ROOT}/css/section2'
SECTION_3_JS = f'{MEDIA_ROOT}/javascript/section3'

FONT_DIR = '/usr/share/fonts/truetype/dejavu'

# --- Palette ---------------------------------------------------------------
# Neutres
NAVY = '#1a2b4c'
GRAY = '#475569'
BG = '#f8f9fb'

# Paires (remplissage, trait) — un accent par famille de concept
BLUE_FILL, BLUE_LINE = '#dbeafe', '#3b82f6'
GREEN_FILL, GREEN_LINE = '#dcfce7', '#22c55e'
ORANGE_FILL, ORANGE_LINE = '#ffedd5', '#f97316'
YELLOW_FILL, YELLOW_LINE = '#fef9c3', '#eab308'
PURPLE_FILL, PURPLE_LINE = '#f3e8ff', '#a855f7'
RED_FILL, RED_LINE = '#fee2e2', '#ef4444'

# Blocs de code (fond sombre)
CODE_BG, CODE_LINE, CODE_TEXT = '#1e293b', '#334155', '#e2e8f0'


# --- Primitives de dessin --------------------------------------------------

def font(size, bold=False, mono=False):
    """Charge une DejaVu. `mono` pour le code, `bold` pour les libellés forts."""
    if mono:
        name = 'DejaVuSansMono-Bold.ttf' if bold else 'DejaVuSansMono.ttf'
    else:
        name = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def text_center(draw, xy, txt, f, fill):
    """Écrit `txt` centré sur `xy`.

    Le décalage par `bbox[1]` compense le jambage supérieur de la police :
    sans lui, deux textes de casse différente ne s'alignent pas.
    """
    x, y = xy
    bbox = draw.textbbox((0, 0), txt, font=f)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x - w / 2, y - h / 2 - bbox[1]), txt, font=f, fill=fill)


def text_left(draw, xy, txt, f, fill):
    """Écrit `txt` aligné à gauche, centré verticalement sur `xy`."""
    x, y = xy
    bbox = draw.textbbox((0, 0), txt, font=f)
    h = bbox[3] - bbox[1]
    draw.text((x, y - h / 2 - bbox[1]), txt, font=f, fill=fill)


def rrect(draw, box, fill, outline, radius=10, width=2):
    """Rectangle à coins arrondis — la forme de base de tous ces schémas."""
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path
