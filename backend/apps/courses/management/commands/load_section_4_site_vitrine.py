"""
Management command — Section 4 : « Créer et mettre en ligne un site vitrine ».

Chapitre **final** du parcours (order_index=4), après HTML (1), CSS (2) et
JavaScript (3). Contrairement aux précédents, c'est un **fil rouge guidé,
réalisé hors application** : l'apprenant installe ses outils, conçoit une
maquette, code un vrai site sur son poste, puis le publie en ligne.

Le cœur du chapitre est un **catalogue des composants et structures de pages**
qu'on retrouve dans presque tous les sites vitrines (navigation, hero, page de
présentation, galerie, contact, footer). Pas d'exercice dans le bac à sable :
tout se code sur le poste de l'apprenant, ce qui est justement l'objet du
chapitre.

Structure d'un ÉCHAFAUDAGE — à compléter leçon par leçon :
  - 4.0 « Ce qu'on va construire » ........... RÉDIGÉ
  - Fondations & composants (théorie) ........ SQUELETTE (objectifs + plan + liens)
  - « Projet : ton site vitrine » ............ RÉDIGÉ (brief + critères)
  - « Quiz de validation » ................... RÉDIGÉ (6 questions)

Les squelettes portent des marqueurs `> 🚧 **À rédiger**` et
`> 🖼️ **Capture à ajouter**` : ils sont navigables en l'état, et signalent
sans ambiguïté ce qui reste à écrire.

Usage :
    python manage.py load_section_4_site_vitrine --force
"""
from django.core.management.base import BaseCommand

from apps.courses.models import Chapter, Lesson, Quiz

CHAPTER_SLUG = "site-vitrine"


class Command(BaseCommand):
    help = "Charge la Section 4 : Créer et mettre en ligne un site vitrine."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Supprime le chapitre 'site-vitrine' existant avant de le recréer.",
        )

    # ------------------------------------------------------------------ #
    # Toutes les leçons de ce chapitre sont de la théorie Markdown.
    # ------------------------------------------------------------------ #
    def _theory(self, chapter, order, title, slug, content, *, duration=20, points=10):
        return Lesson.objects.create(
            chapter=chapter,
            title=title,
            slug=slug,
            lesson_type="THEORY",
            order_index=order,
            content=content,
            estimated_duration=duration,
            points=points,
            is_published=True,
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Chargement de la Section 4 : Site vitrine..."))

        if options.get("force"):
            Chapter.objects.filter(slug=CHAPTER_SLUG).delete()
            self.stdout.write(self.style.WARNING("Ancien chapitre 'site-vitrine' supprimé."))

        chapter = Chapter.objects.create(
            title="Créer et mettre en ligne un site vitrine",
            slug=CHAPTER_SLUG,
            description=(
                "Le grand final : rassemblez tout ce que vous avez appris pour "
                "concevoir, coder et PUBLIER votre premier vrai site — un site "
                "vitrine. On y passe en revue tous les composants classiques "
                "(navigation, hero, galerie, contact, footer) et on met le site "
                "en ligne avec les outils des pros (VSCode, Git, GitHub, Figma)."
            ),
            order_index=4,
            estimated_duration=330,
            is_published=True,
        )
        self.stdout.write(f"✅ Chapitre créé : {chapter.title}")

        # ============================================================== #
        # 4.0 — Ce qu'on va construire (RÉDIGÉ)
        # ============================================================== #
        self._theory(
            chapter, 1,
            "Ce qu'on va construire",
            "site-vitrine-intro",
            duration=15,
            points=5,
            content="""# Ce qu'on va construire 🚀

Bienvenue dans le **chapitre final** ! Jusqu'ici, vous avez écrit du code dans
l'éditeur intégré de la plateforme. Ici, on change de dimension : vous allez
**quitter le bac à sable** pour construire un vrai site, sur **votre propre
ordinateur**, exactement comme le fait un développeur professionnel.

## 🎯 Objectif du chapitre

À la fin, vous aurez **votre premier site vitrine en ligne**, accessible par une
vraie adresse web que vous pourrez partager (à un ami, un recruteur, un client).

## Qu'est-ce qu'un « site vitrine » ?

Un **site vitrine** présente une personne, une activité ou une entreprise sur
quelques sections, sans espace de connexion ni base de données. C'est le projet
d'apprentissage classique — et le plus utile — quand on débute :

- un **portfolio** de développeur ou de designer,
- le site d'un **artisan** ou d'un **restaurant** local,
- la page d'une **association**,
- une **landing page** pour un produit.

## 🧩 Les composants qu'on va apprendre à construire

Ce chapitre est un **catalogue** : chaque leçon présente une brique qu'on
retrouve dans presque tous les sites vitrines, avec sa raison d'être, ses
variantes, et comment la coder.

| Composant | Rôle |
|---|---|
| **Navigation** (navbar, dropdown, sidebar) | Se déplacer dans le site |
| **Hero** | La première impression : titre + bouton d'action |
| **Page de présentation** (à propos / services) | Expliquer qui vous êtes et ce que vous offrez |
| **Galerie / portfolio** | Montrer vos réalisations |
| **Contact** | Un formulaire pour vous joindre |
| **Footer** | Liens, réseaux sociaux, mentions |

> 🖼️ **Capture à ajouter** : un aperçu du site vitrine final (maquette + rendu),
> avec ses différents composants annotés.

## 🗺️ Le parcours de ce chapitre

1. **Installer les outils** (VSCode, un navigateur, Git)
2. **Versionner et publier** avec Git + GitHub Pages
3. **Concevoir la maquette** avec Figma et Canva
4. **L'ossature** d'une page en HTML sémantique
5. **Les composants** un par un : navigation, hero, présentation, galerie, contact, footer
6. **Responsive & finitions**
7. **Mise en ligne**
8. **Votre propre site** (projet final)

## ✅ Prérequis

Avoir terminé les chapitres **HTML**, **CSS** et **JavaScript** de la
plateforme. On s'appuie sur ces bases — on ne les réapprend pas.

---

Prêt ? On commence par équiper votre poste de travail. 👉
""",
        )

        # ============================================================== #
        # FONDATIONS
        # ============================================================== #
        self._theory(
            chapter, 2,
            "Préparer son poste : VSCode & navigateur",
            "site-vitrine-poste",
            duration=40,
            points=15,
            content="""# Préparer son poste de travail 🛠️

Jusqu'ici, vous écriviez votre code dans l'éditeur de la plateforme, qui
s'occupait de tout. Pour construire un vrai site, vous allez installer sur
**votre ordinateur** les mêmes outils qu'un développeur professionnel. Bonne
nouvelle : ils sont **gratuits**, et cette installation ne se fait **qu'une
seule fois**.

Prenez votre temps sur cette leçon : un poste bien réglé, c'est des heures
gagnées sur tout le reste du chapitre.

## 🎯 Objectifs

À la fin de cette leçon, vous saurez :

- ✅ installer **Visual Studio Code**, l'éditeur de code de référence
- ✅ vous repérer dans son interface
- ✅ installer les **extensions** qui font gagner un temps fou
- ✅ écrire une première page et la **voir en direct** dans le navigateur
- ✅ ouvrir et lire les **outils de développement** (DevTools) du navigateur
- ✅ organiser un **dossier de projet** proprement

---

## 1. Le trio de l'atelier web

Pour faire du web, il faut trois choses :

| Outil | Rôle | On l'installe… |
|---|---|---|
| **Un navigateur** | Afficher et tester le site | Vous l'avez déjà (Chrome, Firefox, Edge…) |
| **Un éditeur de code** | Écrire le code confortablement | Maintenant : **VSCode** |
| **Git** | Sauvegarder et publier | Au chapitre suivant |

> 💡 Un fichier HTML est un **simple fichier texte**. On pourrait l'écrire dans
> le Bloc-notes… mais un vrai éditeur colore le code, signale les erreurs et
> complète les balises. D'où VSCode.

---

## 2. Installer Visual Studio Code

**Visual Studio Code** (souvent abrégé **VSCode**) est l'éditeur de code le plus
utilisé au monde. Léger, gratuit, disponible sur Windows, macOS et Linux.

### Étapes

1. Rendez-vous sur le site officiel : **https://code.visualstudio.com/**
2. Cliquez sur le gros bouton de téléchargement — le site détecte votre système
   d'exploitation automatiquement.
3. Installez :

   - **Windows** : ouvrez le fichier `.exe` téléchargé et suivez l'assistant.
     👉 Cochez **« Ajouter l'action Ouvrir avec Code »** et **« Ajouter à
     PATH »** : cela vous permettra d'ouvrir un dossier dans VSCode d'un clic
     droit.
   - **macOS** : ouvrez le `.zip`, puis **glissez** l'application
     *Visual Studio Code* dans le dossier **Applications**.
   - **Linux** : installez le paquet `.deb` / `.rpm`, ou via le gestionnaire de
     paquets de votre distribution.

4. Lancez VSCode. Au premier démarrage, vous pouvez choisir un **thème** de
   couleurs (clair ou sombre) — purement esthétique.

> 🖼️ **Capture à ajouter** : la page de téléchargement officielle + la fenêtre
> de bienvenue de VSCode au premier lancement.

> ⚠️ Ne confondez pas **Visual Studio Code** (l'éditeur léger qu'on installe) et
> **Visual Studio** (un énorme logiciel pour d'autres langages). On veut bien
> **Code**.

### Passer l'interface en français (facultatif)

VSCode est en anglais par défaut. Pour le franciser : ouvrez la **palette de
commandes** avec `Ctrl+Shift+P` (macOS : `Cmd+Shift+P`), tapez
`Configure Display Language`, choisissez **Français**, installez le module de
langue proposé, puis redémarrez.

---

## 3. Se repérer dans VSCode

Ouvrez VSCode : au début, l'écran peut impressionner. En réalité, quatre zones
suffisent pour commencer.

- **La barre d'activité** (tout à gauche) : les icônes pour basculer entre
  l'explorateur de fichiers, la recherche, le contrôle de version (Git), les
  extensions…
- **L'explorateur** : l'arborescence des fichiers de votre projet.
- **L'éditeur** (au centre) : là où vous tapez votre code, avec des onglets.
- **Le terminal intégré** (en bas, à ouvrir avec ``Ctrl+ù`` ou via le menu
  *Terminal → Nouveau terminal*) : pour taper des commandes (utile au chapitre
  Git).

### Deux réflexes à prendre tout de suite

- **Ouvrir un dossier** : *Fichier → Ouvrir le dossier…* (ou glissez un dossier
  sur la fenêtre). ⚠️ On travaille **toujours en ouvrant un dossier**, jamais un
  fichier isolé — sinon des outils comme Live Server ne fonctionneront pas.
- **La palette de commandes** : `Ctrl+Shift+P`. C'est le couteau suisse : tout
  ce que fait VSCode est accessible en tapant son nom ici.

---

## 4. Les extensions indispensables

Les **extensions** ajoutent des super-pouvoirs à VSCode. On les installe depuis
l'icône **Extensions** de la barre d'activité (ou `Ctrl+Shift+X`) : on cherche
le nom, on clique sur **Installer**.

Installez ces trois-là (les incontournables du débutant en web) :

| Extension | Ce qu'elle apporte |
|---|---|
| **Live Server** *(par Ritwick Dey)* | Ouvre votre page dans le navigateur et la **rafraîchit automatiquement** à chaque enregistrement |
| **Prettier — Code formatter** | **Met en forme** votre code proprement d'un clic |
| **Auto Rename Tag** | Renomme automatiquement la balise fermante quand vous modifiez l'ouvrante |

> 💡 **Bonus esthétique/confort** (facultatif) : *Material Icon Theme* (jolies
> icônes de fichiers) et *indent-rainbow* (colore l'indentation).

### Régler Prettier pour formater à l'enregistrement

Un réglage qui change la vie : demander à VSCode de **formater le code chaque
fois que vous sauvegardez**.

1. `Ctrl+Shift+P` → tapez `Preferences: Open User Settings` → Entrée.
2. Dans la barre de recherche des réglages, tapez **Format On Save** et
   **cochez** la case.
3. Cherchez **Default Formatter** et choisissez **Prettier**.

Désormais, à chaque `Ctrl+S`, votre code s'aligne tout seul. 🎉

---

## 5. Votre première page, en direct 🔴

Assez de théorie : créons une page et voyons-la s'afficher.

1. Créez quelque part un dossier nommé **`mon-site-vitrine`**.
2. Dans VSCode : *Fichier → Ouvrir le dossier…* et choisissez ce dossier.
3. Dans l'explorateur, cliquez sur l'icône **Nouveau fichier** et nommez-le
   **`index.html`**.
4. Collez ce contenu :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mon premier site</title>
</head>
<body>
  <h1>Bonjour, le web ! 👋</h1>
  <p>Ceci est ma toute première page, sur mon propre ordinateur.</p>
</body>
</html>
```

5. Enregistrez (`Ctrl+S`).
6. **Clic droit** sur `index.html` → **« Open with Live Server »** (ou le bouton
   **Go Live** en bas à droite de VSCode).

Votre navigateur s'ouvre sur `http://127.0.0.1:5500` et affiche la page. Le
plus magique : **modifiez le titre, enregistrez → la page se met à jour toute
seule**, sans même rafraîchir. C'est votre boucle de travail pour tout le
chapitre.

> 💡 `index.html` est un nom spécial : c'est la **page d'accueil** par défaut
> d'un site. On la retrouvera à la mise en ligne.

---

## 6. Le navigateur et ses outils de développement (DevTools)

Le navigateur n'est pas qu'une fenêtre : il embarque des **outils de
développement** puissants. On les ouvre avec **`F12`**, ou par **clic droit →
Inspecter**.

Les onglets à connaître dès maintenant :

- **Éléments** (*Elements*) : montre le HTML et le CSS de la page **en direct**.
  Vous pouvez survoler un élément pour le repérer, et même modifier le style à la
  volée pour tester (ces changements sont temporaires).
- **Console** : affiche les **messages et erreurs** — indispensable quand un
  script JavaScript ne marche pas.
- **Réseau** (*Network*) : liste tout ce que la page télécharge (images, styles).

### Tester l'affichage mobile 📱

Toujours dans les DevTools, cliquez sur l'icône **« Toggle device toolbar »**
(un petit téléphone/tablette, ou `Ctrl+Shift+M`). Vous pouvez alors simuler un
écran de téléphone et vérifier que le site reste lisible. On s'en servira
beaucoup pour le **responsive**.

> 🖼️ **Capture à ajouter** : les DevTools ouverts sur l'onglet Éléments + la
> barre d'outils d'appareil (mode mobile).

---

## 7. Organiser son dossier de projet

Un projet bien rangé se maintient sans douleur. Voici la structure de départ
qu'on adoptera :

```text
mon-site-vitrine/
├── index.html          ← la page d'accueil
├── css/
│   └── style.css       ← les styles
├── js/
│   └── script.js       ← le JavaScript (menu, interactions)
└── assets/
    └── images/         ← vos images
```

### Règles de nommage (à respecter absolument)

- **Pas d'espaces** ni d'**accents** dans les noms de fichiers et de dossiers :
  `ma-page.html` ✅, `Ma Page à Moi.html` ❌.
- **Tout en minuscules**, et des **tirets** `-` pour séparer les mots
  (`a-propos.html`).
- Des noms **explicites** : `logo.svg` vaut mieux que `img1.svg`.

> ⚠️ Le web est **sensible à la casse** sur les serveurs : `Photo.JPG` et
> `photo.jpg` sont deux fichiers différents une fois en ligne. Prenez
> l'habitude du tout-minuscule dès maintenant, ça évite des liens cassés
> mystérieux à la mise en ligne.

---

## ✅ Récapitulatif

Cochez mentalement — vous devez pouvoir :

- [ ] ouvrir VSCode et y **ouvrir un dossier** ;
- [ ] installer une **extension** (Live Server, Prettier, Auto Rename Tag) ;
- [ ] créer un `index.html` et le voir **en direct** avec Live Server ;
- [ ] ouvrir les **DevTools** (`F12`) et passer en **mode mobile** ;
- [ ] ranger vos fichiers selon la structure ci-dessus, sans espaces ni accents.

Si tout cela est acquis, votre atelier est prêt. 🧰

---

## 🧭 Prochaine étape

Vous savez écrire et prévisualiser une page. Il manque deux choses avant de
construire : **sauvegarder l'historique** de votre travail et **le mettre en
ligne**. C'est l'objet de la leçon suivante : **Git, GitHub & GitHub Pages**. 👉
""",
        )

        self._theory(
            chapter, 3,
            "Versionner & publier : Git, GitHub & GitHub Pages",
            "site-vitrine-git-github",
            duration=45,
            points=20,
            content="""# Versionner et publier : Git & GitHub 🐙

Vous avez déjà connu ça : `projet.html`, puis `projet-v2.html`, puis
`projet-final.html`, puis `projet-final-VRAI.html`… et le lendemain, plus moyen
de savoir lequel est le bon. **Git** met fin à ce cauchemar : il garde
l'**historique complet** de votre travail, comme une machine à remonter le
temps. Et **GitHub** met cet historique dans le cloud — et, cerise sur le
gâteau, **héberge votre site gratuitement**.

C'est la leçon la plus « nouvelle » du chapitre. Allez-y pas à pas, tapez les
commandes vous-même : c'est en le faisant que ça rentre.

## 🎯 Objectifs

À la fin de cette leçon, vous saurez :

- ✅ comprendre **à quoi sert Git** (et la différence avec **GitHub**)
- ✅ **installer** et **configurer** Git
- ✅ enregistrer votre travail avec le cycle **`add` → `commit`**
- ✅ créer un compte **GitHub** et y **envoyer** votre code (`push`)
- ✅ **publier votre site en ligne** avec **GitHub Pages**
- ✅ **mettre à jour** votre site en une commande

---

## 1. Git ou GitHub ? Ne confondons pas

C'est LA confusion du débutant, réglons-la tout de suite :

| | Quoi | Où |
|---|---|---|
| **Git** | Le **logiciel** qui suit l'historique de vos fichiers | Sur **votre ordinateur** |
| **GitHub** | Un **service en ligne** qui héberge vos dépôts Git | Sur **le cloud** (site web) |

> 💡 Analogie : **Git** est comme la fonction « historique des versions » d'un
> document ; **GitHub** est comme le Google Drive où vous déposez ce document
> pour le sauvegarder et le partager. On peut utiliser Git seul, mais GitHub
> apporte la sauvegarde, le partage… et l'hébergement gratuit.

Un projet suivi par Git s'appelle un **dépôt** (*repository*, ou « repo »).

---

## 2. Installer Git

1. Rendez-vous sur **https://git-scm.com/** et téléchargez la version de votre
   système.

   - **Windows** : lancez l'installeur. Vous pouvez **laisser toutes les options
     par défaut** (elles sont bonnes). Bonus : l'installation fournit
     **Git Bash**, un terminal pratique.
   - **macOS** : le plus simple est de taper `git --version` dans le Terminal —
     macOS proposera d'installer les outils de développement. Sinon, l'installeur
     du site fonctionne.
   - **Linux** : `sudo apt install git` (Debian/Ubuntu) ou l'équivalent de votre
     distribution.

2. **Vérifiez** l'installation. Ouvrez un terminal (dans VSCode :
   *Terminal → Nouveau terminal*) et tapez :

```bash
git --version
```

Si un numéro de version s'affiche (ex. `git version 2.45.0`), c'est gagné. ✅

---

## 3. Se présenter à Git (une seule fois)

Chaque enregistrement (commit) est **signé** par son auteur. Dites donc à Git
qui vous êtes — à faire **une seule fois** sur votre machine :

```bash
git config --global user.name "Votre Prénom Nom"
git config --global user.email "votre@email.com"
```

> 💡 Utilisez **le même e-mail** que celui de votre futur compte GitHub : vos
> contributions y seront correctement associées.

---

## 4. Le modèle mental de Git : trois zones

Avant de taper des commandes, visualisez ce que fait Git. Vos fichiers passent
par **trois zones** :

```text
  Vos fichiers            Zone de préparation           Historique
 (répertoire de   ──►      (« staging »)          ──►    (dépôt)
   travail)            git add                     git commit
```

- **Répertoire de travail** : vos fichiers, tels que vous les modifiez.
- **Zone de préparation** (*staging*) : ce que vous **choisissez** d'inclure
  dans le prochain enregistrement — on y met les fichiers avec `git add`.
- **Historique** (le dépôt) : les enregistrements figés, créés par `git commit`.

Un **commit**, c'est donc un **point de sauvegarde** daté, signé, accompagné
d'un petit message qui décrit ce que vous avez fait.

---

## 5. Créer le dépôt et faire son premier commit

Ouvrez le terminal **dans le dossier de votre projet** (`mon-site-vitrine`).
Dans VSCode, le terminal s'ouvre déjà au bon endroit.

### a) Initialiser le dépôt

```bash
git init
```

Git crée un dossier caché `.git/` : votre projet est désormais **suivi**.

### b) Voir l'état

```bash
git status
```

Git liste vos fichiers en « non suivis » (en rouge). Normal, on vient de
commencer.

### c) Préparer puis enregistrer

```bash
git add .
git commit -m "Première version de mon site vitrine"
```

- `git add .` : place **tous** les fichiers modifiés dans la zone de
  préparation (le `.` signifie « tout le dossier courant »).
- `git commit -m "…"` : fige un point de sauvegarde avec un **message clair**.

> 💡 **Un bon message de commit** décrit ce que le commit apporte, à
> l'impératif ou au présent : *« Ajoute la section hero »*, *« Corrige le menu
> mobile »*. Évitez *« modifs »* ou *« truc »* — le futur vous dira merci.

> 🖱️ **Sans le terminal ?** VSCode possède un onglet **Contrôle de code source**
> (icône de branche dans la barre d'activité) : on y coche les fichiers, on
> tape un message et on valide en un clic. Les commandes et l'interface font
> exactement la même chose.

---

## 6. Ignorer ce qui ne doit pas être versionné : `.gitignore`

Certains fichiers ne doivent **pas** entrer dans l'historique (fichiers système,
dossiers d'outils…). On les liste dans un fichier nommé **`.gitignore`** à la
racine du projet :

```text
# Fichiers système
.DS_Store
Thumbs.db

# Dossiers d'outils / dépendances
node_modules/
```

Pour un simple site vitrine en HTML/CSS/JS, un `.gitignore` minimal comme
ci-dessus suffit largement.

---

## 7. Créer un compte GitHub et un dépôt distant

1. Créez un compte gratuit sur **https://github.com/**.
2. Cliquez sur **New repository** (bouton vert, ou le **+** en haut à droite).
3. Renseignez :
   - **Repository name** : `mon-site-vitrine` (le même nom que votre dossier,
     c'est plus clair) ;
   - laissez-le **Public** (obligatoire pour l'hébergement gratuit GitHub
     Pages) ;
   - **ne cochez rien d'autre** (pas de README, pas de .gitignore) : votre
     projet local a déjà tout, on veut éviter les conflits au premier envoi.
4. Cliquez sur **Create repository**. GitHub affiche alors une page avec des
   commandes : c'est ce qu'on fait juste après.

> 🖼️ **Capture à ajouter** : le formulaire de création de dépôt sur GitHub.

---

## 8. Relier le local au distant, puis envoyer (`push`)

De retour dans le terminal, dans votre projet :

```bash
git branch -M main
git remote add origin https://github.com/<votre-pseudo>/mon-site-vitrine.git
git push -u origin main
```

Décryptage :

- `git branch -M main` : nomme votre branche principale **`main`** (le standard
  actuel).
- `git remote add origin …` : enregistre l'adresse du dépôt GitHub sous le
  surnom **`origin`**. ⚠️ Remplacez `<votre-pseudo>` par votre vrai pseudo
  GitHub (l'URL est affichée sur la page du dépôt).
- `git push -u origin main` : **envoie** vos commits vers GitHub. Le `-u` mémorise
  le lien, si bien que les prochaines fois un simple `git push` suffira.

> 🔐 **Authentification** : au premier `push`, Git vous demande de vous
> connecter à GitHub. Sur Windows/macOS, une fenêtre de navigateur s'ouvre pour
> valider — le mot de passe de compte **ne fonctionne plus** pour Git. Si l'on
> vous réclame un mot de passe dans le terminal, créez un **jeton d'accès
> personnel** (*Personal Access Token*) depuis
> *GitHub → Settings → Developer settings → Tokens* et collez-le à la place du
> mot de passe.

Rafraîchissez la page de votre dépôt sur GitHub : vos fichiers y sont ! 🎉

---

## 9. 🚀 Mettre le site en ligne avec GitHub Pages

C'est le moment magique : publier gratuitement, sans serveur.

1. Sur GitHub, ouvrez votre dépôt → onglet **Settings**.
2. Menu de gauche → **Pages**.
3. Sous **Build and deployment**, section **Source** : choisissez
   **Deploy from a branch**.
4. Sélectionnez la branche **`main`** et le dossier **`/ (root)`**, puis
   **Save**.
5. Patientez une minute, rafraîchissez : GitHub affiche l'adresse de votre site,
   du type :

```text
https://<votre-pseudo>.github.io/mon-site-vitrine/
```

Ouvrez ce lien : **votre site est en ligne**, accessible depuis n'importe quel
appareil dans le monde. 🌍

> 💡 GitHub Pages sert automatiquement le fichier **`index.html`** à la racine :
> c'est pour cela qu'on a nommé ainsi notre page d'accueil.

> 🖼️ **Capture à ajouter** : l'écran *Settings → Pages* avec la branche
> sélectionnée, et le bandeau vert affichant l'URL du site.

---

## 10. Mettre à jour son site : la boucle du quotidien

À partir de maintenant, publier une modification tient en **trois commandes**.
Vous modifiez votre code, vous enregistrez, puis :

```bash
git add .
git commit -m "Améliore la section contact"
git push
```

Quelques secondes plus tard, **votre site en ligne se met à jour tout seul**.
C'est le rythme que vous garderez jusqu'à la fin du projet : *coder → commit →
push*.

---

## ✅ Récapitulatif

Vous devez pouvoir :

- [ ] expliquer la différence entre **Git** (local) et **GitHub** (en ligne) ;
- [ ] avoir installé et **configuré** Git (`user.name`, `user.email`) ;
- [ ] créer un dépôt et enregistrer un travail avec **`git add`** + **`git commit`** ;
- [ ] envoyer votre code sur GitHub avec **`git push`** ;
- [ ] avoir votre **site en ligne** via **GitHub Pages** ;
- [ ] publier une mise à jour avec **add → commit → push**.

Bravo : vous avez un site accessible à une vraie adresse, et un historique
propre de votre travail. 🏆

---

## 🧭 Prochaine étape

Les outils sont prêts et la publication maîtrisée. Avant de coder pour de bon,
on **dessine** : place à la **maquette** avec **Figma** et **Canva**. 👉
""",
        )

        self._theory(
            chapter, 4,
            "Concevoir la maquette : Figma & Canva",
            "site-vitrine-maquette",
            duration=40,
            points=15,
            content="""# Concevoir avant de coder : la maquette 🎨

On ne construit pas une maison en posant des briques au hasard : on commence
par un **plan**. Pour un site, ce plan s'appelle une **maquette**. La réaliser
avant d'écrire la moindre ligne de code vous fera gagner un temps fou et
donnera un résultat bien plus soigné.

Dans cette leçon, on utilise deux outils gratuits et complémentaires :
**Figma** pour dessiner la structure et le style du site, et **Canva** pour
créer les visuels (logo, bannières).

## 🎯 Objectifs

À la fin de cette leçon, vous saurez :

- ✅ pourquoi **maquetter avant de coder**
- ✅ distinguer un **wireframe** d'une **maquette** finalisée
- ✅ appliquer les **fondamentaux du design** (couleurs, typo, espacement)
- ✅ dessiner votre site dans **Figma**
- ✅ créer vos **visuels** avec **Canva**
- ✅ choisir une **palette**, des **polices** et des **images libres de droits**

---

## 1. Pourquoi maquetter d'abord ?

Coder directement, « on verra bien », est le piège classique : on tâtonne, on
réécrit, on n'est jamais content. La maquette règle ce problème.

- On prend **toutes les décisions visuelles à l'avance** : disposition,
  couleurs, polices, images.
- Déplacer un bloc dans Figma prend **10 secondes** ; le refaire en CSS peut
  prendre 10 minutes.
- On obtient une **cible claire** à reproduire : coder devient « recopier la
  maquette », c'est beaucoup plus simple.

> 💡 Règle d'or : **décider dans Figma, exécuter dans le code.** Chaque hésitation
> résolue avant de coder est du temps gagné.

---

## 2. Wireframe puis maquette : deux niveaux de détail

On dessine en **deux temps**, du plus simple au plus fini :

| | **Wireframe** | **Maquette** (*mockup*) |
|---|---|---|
| Fidélité | Basse | Haute |
| Contenu | Des **blocs gris** | Vraies couleurs, polices, images |
| Question posée | *Qu'est-ce qui va où ?* | *À quoi ça ressemble ?* |

Commencez **toujours par le wireframe** : des rectangles gris pour poser la
**structure** (où est le menu, le hero, les sections…). Une fois la structure
validée, on l'**habille** pour obtenir la maquette.

> 🖼️ **Capture à ajouter** : côte à côte, le wireframe en blocs gris et la
> maquette habillée du même site.

---

## 3. Les fondamentaux du design (pour débuter sans être designer)

Pas besoin d'être artiste. Quatre principes suffisent pour un rendu propre.

### 🎨 La couleur

Limitez-vous à **2 ou 3 couleurs**, réparties selon la règle **60 / 30 / 10** :

- **60 %** une couleur dominante (souvent un neutre : blanc, gris clair),
- **30 %** une couleur secondaire,
- **10 %** une couleur d'**accent** (pour les boutons, les liens importants).

### 🔤 La typographie

**Une police pour les titres**, **une pour le texte**, pas plus. Soignez la
**hiérarchie** : un `h1` bien plus gros que le texte courant, des sous-titres
intermédiaires. Une bonne hiérarchie rend une page lisible d'un coup d'œil.

### 📏 L'espacement (la respiration)

Le **vide** n'est pas de la place perdue : des marges généreuses et régulières
donnent un air professionnel. Gardez des espacements **cohérents** entre les
sections.

### 🖼️ Les images

Des images **nettes et cohérentes** entre elles (même ambiance) valent mieux
qu'un patchwork. Une image de mauvaise qualité déclasse tout le site.

---

## 4. Dessiner sa maquette avec Figma

**Figma** est l'outil de maquettage le plus utilisé par les professionnels.
Gratuit, il fonctionne **directement dans le navigateur**.

1. Créez un compte gratuit sur **https://www.figma.com/** et cliquez sur
   **New design file**.
2. Créez un **cadre** (*Frame*, touche `F`) : Figma propose des tailles toutes
   prêtes. Prenez-en **deux** :
   - un **Desktop** (par ex. 1440 px de large),
   - un **Mobile** (par ex. 375 px) — pour penser le responsive dès le départ.
3. Les outils de base à connaître :
   - **Rectangle** (`R`) : pour les blocs (sections, cartes, images).
   - **Texte** (`T`) : pour les titres et paragraphes.
   - Le panneau de droite : couleurs, taille, police, coins arrondis…
4. **Étape 1 — le wireframe** : remplissez vos cadres de **rectangles gris**,
   un par section (menu, hero, à propos, services, galerie, contact, footer).
5. **Étape 2 — la maquette** : appliquez votre palette, vos polices, glissez de
   vraies images. Votre site prend vie.

> 💡 **Astuce** : dès qu'un élément se répète (un bouton, une carte), Figma
> permet d'en faire un **composant** réutilisable. Pas indispensable au début,
> mais très pratique.

---

## 5. Créer ses visuels avec Canva

Figma sert à agencer ; **Canva** sert à **fabriquer des visuels** rapidement,
sans compétences en graphisme, à partir de milliers de modèles.

Utilisez Canva pour :

- un **logo** simple,
- une **bannière** ou une image de fond de hero,
- des **visuels pour les réseaux sociaux**,
- des **icônes** et illustrations.

Créez votre visuel sur **https://www.canva.com/**, puis **exportez-le** (PNG,
ou **SVG** pour un logo qui reste net à toute taille) et rangez-le dans
`assets/images/`.

> 💡 **Figma ou Canva ?** Figma = **structurer** l'écran (la mise en page du
> site). Canva = **produire un visuel** isolé (un logo, une bannière). Les deux
> se complètent.

---

## 6. Choisir couleurs, polices et images

### Une palette de couleurs

Partez d'un générateur comme **coolors.co** pour obtenir une palette
harmonieuse, et notez les **codes hexadécimaux** (ex. `#5b3df0`) : on les
réutilisera tels quels en CSS. Vérifiez le **contraste** texte/fond (un texte
gris clair sur blanc est illisible).

### Des polices

Piochez sur **Google Fonts** (gratuit) : choisissez **un couple** qui fonctionne
(par ex. un titre marqué + un texte neutre et lisible). Notez leurs noms : au
chapitre CSS, on les importera dans le site.

### Des images libres de droits

Téléchargez sur **Unsplash** ou **Pexels** : des photos gratuites, utilisables
même pour un projet publié.

> ⚠️ **N'utilisez jamais** une image trouvée au hasard sur Google : la plupart
> sont **protégées par le droit d'auteur**. Restez sur les banques d'images
> libres.

Pour les **icônes** (réseaux sociaux, services), pensez à des bibliothèques
comme **Font Awesome** ou **Lucide** — on verra comment les intégrer.

---

## 7. Maquetter NOTRE site vitrine

Concrètement, préparez dans Figma les sections qu'on va coder ensemble dans les
prochaines leçons :

- une **navigation** (logo + liens) ;
- un **hero** (titre, accroche, bouton) ;
- une section **à propos** ;
- une grille de **services** (3 cartes) ;
- une **galerie** de réalisations ;
- une section **contact** ;
- un **footer**.

Chaque bloc de votre maquette correspondra à une leçon du chapitre : vous
n'aurez plus qu'à le reproduire en code. 🧩

---

## ✅ Récapitulatif

Vous devez pouvoir :

- [ ] expliquer **pourquoi** on maquette avant de coder ;
- [ ] réaliser un **wireframe** (blocs gris) puis une **maquette** habillée ;
- [ ] respecter les bases : **2-3 couleurs**, **2 polices**, de la
      **respiration** ;
- [ ] dessiner vos écrans dans **Figma** (desktop + mobile) ;
- [ ] créer un visuel dans **Canva** et l'exporter ;
- [ ] réunir une **palette**, des **polices** et des **images libres**.

Avec une maquette claire en main, coder ne sera plus qu'une formalité. 🎯

---

## 🧭 Prochaine étape

On passe enfin au code : on construit l'**ossature HTML sémantique** de la page,
prête à recevoir tous les composants de la maquette. 👉
""",
        )

        self._theory(
            chapter, 5,
            "L'ossature d'une page : HTML sémantique",
            "site-vitrine-structure",
            duration=35,
            points=15,
            content="""# L'ossature d'une page : HTML sémantique 🏗️

Avant de poser les jolis composants, il faut le **squelette** : la structure de
la page, écrite avec des balises qui ont du **sens**. Un bon squelette, c'est le
gros œuvre d'une maison : invisible une fois habillé, mais tout tient dessus.

## 🎯 Objectifs

À la fin de cette leçon, vous saurez :

- ✅ ce que veut dire **HTML « sémantique »** et pourquoi ça compte
- ✅ le rôle des grandes balises `header`, `nav`, `main`, `section`, `footer`
- ✅ construire l'**ossature complète** de votre site vitrine
- ✅ relier la navigation aux sections grâce aux **ancres** (`id`)

---

## 1. HTML « sémantique », ça veut dire quoi ?

Une balise **sémantique** décrit le **sens** de son contenu, pas seulement son
apparence. Comparez :

```html
<!-- Non sémantique : des boîtes neutres -->
<div class="haut">…</div>
<div class="milieu">…</div>
<div class="bas">…</div>

<!-- Sémantique : chaque balise dit ce qu'elle contient -->
<header>…</header>
<main>…</main>
<footer>…</footer>
```

Les deux s'affichent pareil. Mais la seconde version est **comprise** par la
machine. Pourquoi c'est important :

- ♿ **Accessibilité** : les lecteurs d'écran (utilisés par les personnes
  malvoyantes) annoncent « bannière », « navigation », « contenu principal » et
  permettent d'y sauter directement.
- 🔍 **Référencement (SEO)** : Google comprend mieux la structure de la page et
  la classe mieux.
- 👓 **Lisibilité** : *vous* relisez votre code bien plus facilement.

> 💡 Règle simple : **s'il existe une balise qui décrit ce que je mets, je
> l'utilise.** On garde `<div>` pour les regroupements purement visuels (voir
> plus bas).

---

## 2. Rappel : le squelette de base

Toute page HTML repart de cette base (vue au chapitre HTML) :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Site vitrine de Studio Lumière, photographe.">
  <title>Studio Lumière — Photographe</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <!-- Tout le contenu visible vient ici -->

  <script src="js/script.js"></script>
</body>
</html>
```

- Le `<head>` contient les **métadonnées** (invisibles) : encodage, responsive,
  description pour le SEO, titre de l'onglet, lien vers le CSS.
- Le `<body>` contient le **contenu visible**.
- Le `<script>` est placé **juste avant `</body>`** pour que le JavaScript
  s'exécute une fois la page chargée.

---

## 3. Les grandes balises sémantiques

Voici celles qu'on utilise pour structurer un site vitrine :

| Balise | Rôle |
|---|---|
| `<header>` | L'en-tête du site (logo + navigation) |
| `<nav>` | Un bloc de **navigation** (les liens du menu) |
| `<main>` | Le **contenu principal** de la page (unique) |
| `<section>` | Une **section** thématique (à propos, services…) |
| `<article>` | Un contenu **autonome** (une carte projet, un témoignage) |
| `<aside>` | Un contenu **annexe** (barre latérale, encadré) |
| `<footer>` | Le **pied de page** |
| `<h1>`…`<h6>` | La **hiérarchie des titres** |

Trois règles à respecter :

1. **Un seul `<main>`** par page.
2. **Un seul `<h1>`** par page (le titre principal), puis `<h2>` pour les
   sections, `<h3>` pour les sous-parties… sans **sauter** de niveau.
3. `<header>` et `<footer>` encadrent la page ; `<main>` contient tout le reste.

---

## 4. Construire l'ossature de notre site vitrine

Voici la **colonne vertébrale** qu'on va remplir tout au long du chapitre.
Chaque `<section>` a un **`id`** (on verra pourquoi juste après) et attend son
composant :

```html
<body>
  <!-- EN-TÊTE : logo + navigation (leçon Navigation) -->
  <header class="site-header">
    <nav class="navbar">
      <!-- logo + liens -->
    </nav>
  </header>

  <main>
    <!-- HERO : accroche + bouton (leçon Hero) -->
    <section id="accueil" class="hero">
    </section>

    <!-- À PROPOS (leçon Présentation) -->
    <section id="apropos" class="about">
    </section>

    <!-- SERVICES : grille de cartes (leçon Présentation) -->
    <section id="services" class="services">
    </section>

    <!-- GALERIE / PORTFOLIO (leçon Galerie) -->
    <section id="galerie" class="gallery">
    </section>

    <!-- CONTACT : formulaire (leçon Contact) -->
    <section id="contact" class="contact">
    </section>
  </main>

  <!-- PIED DE PAGE (leçon Footer) -->
  <footer class="site-footer">
  </footer>

  <script src="js/script.js"></script>
</body>
```

> 🖼️ **Capture à ajouter** : l'ossature en blocs (comme le wireframe) à côté du
> code, pour visualiser la correspondance section ↔ balise.

Gardez ce fichier : les prochaines leçons viendront **remplir chaque section**,
une par une.

---

## 5. `<div>` a-t-il encore sa place ? Oui.

La balise `<div>` n'a **aucun sens** particulier : c'est une boîte neutre. On
l'utilise justement quand **il n'y a pas de sens** à exprimer, seulement un
besoin de **regrouper pour le style** — par exemple un conteneur qui centre le
contenu :

```html
<section id="apropos" class="about">
  <div class="container">
    <!-- texte + image, regroupés pour la mise en page -->
  </div>
</section>
```

> 💡 En résumé : **`<section>`, `<nav>`, `<article>`… quand il y a un sens ;
> `<div>` quand c'est juste de la mise en page.**

---

## 6. Les ancres : relier la navigation aux sections

Pourquoi ces `id` sur chaque section ? Parce qu'un site vitrine tient souvent
sur **une seule page** : cliquer sur « Contact » dans le menu ne change pas de
page, mais **fait défiler** jusqu'à la bonne section.

Le mécanisme est natif en HTML : un lien vers `#contact` saute vers l'élément
dont l'`id` est `contact`.

```html
<a href="#contact">Contact</a>   <!-- saute vers… -->
<section id="contact"> … </section>
```

C'est exactement ce qu'utilisera notre menu. On ajoutera même un **défilement
doux** (`scroll-behavior: smooth`) dans la prochaine leçon pour que le saut soit
fluide.

---

## ✅ Récapitulatif

Vous devez pouvoir :

- [ ] expliquer ce qu'est le HTML **sémantique** et ses 3 bénéfices
      (accessibilité, SEO, lisibilité) ;
- [ ] citer le rôle de `header`, `nav`, `main`, `section`, `footer` ;
- [ ] respecter : **un seul `<main>`**, **un seul `<h1>`**, hiérarchie des
      titres sans saut ;
- [ ] avoir écrit l'**ossature complète** de votre site avec un `id` par
      section ;
- [ ] comprendre le lien **ancre `#id` ↔ section** pour la navigation.

L'ossature est debout. Il ne reste plus qu'à l'habiller, composant par
composant. 🧱

---

## 🧭 Prochaine étape

On attaque le premier composant, et non des moindres : la **navigation**
(navbar responsive, menu déroulant, sidebar). 👉
""",
        )

        # ============================================================== #
        # NAVIGATION
        # ============================================================== #
        self._theory(
            chapter, 6,
            "La navigation : navbar, menu déroulant & sidebar",
            "site-vitrine-navigation",
            duration=55,
            points=25,
            content="""# La navigation 🧭

La navigation, c'est ce qui permet à un visiteur de **se déplacer** dans votre
site. C'est le premier composant qu'on remarque, et souvent celui qui trahit un
site amateur quand il est mal fait. On va le soigner.

On construit ici les **trois formes** les plus courantes, avec leur code
complet : la **navbar** (barre du haut) et son **menu burger** pour le mobile,
les **menus déroulants** (dropdown), et la **barre latérale** (sidebar).

## 🎯 Objectifs

À la fin de cette leçon, vous saurez coder :

- ✅ une **navbar** horizontale, **collante** et avec **défilement doux**
- ✅ un **menu burger** fonctionnel sur mobile (avec un peu de JavaScript)
- ✅ un **menu déroulant** (dropdown) pour les sous-rubriques
- ✅ une **barre latérale** (sidebar) qui glisse depuis le bord
- ✅ le tout **accessible** (clavier + lecteurs d'écran)

---

## 1. La barre de navigation (navbar)

La navbar est la barre horizontale en haut du site : **logo à gauche, liens à
droite**. Sur un site vitrine d'une seule page, ses liens sont des **ancres**
vers les sections (`#apropos`, `#contact`…), comme vu à la leçon précédente.

### a) La structure HTML

On reprend le `<header>` de notre ossature :

```html
<header class="site-header">
  <nav class="navbar">
    <a href="#accueil" class="nav-logo">Studio Lumière</a>

    <button class="nav-toggle" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="nav-menu">
      ☰
    </button>

    <ul id="nav-menu" class="nav-links">
      <li><a href="#apropos">À propos</a></li>
      <li><a href="#services">Services</a></li>
      <li><a href="#galerie">Galerie</a></li>
      <li><a href="#contact" class="nav-cta">Contact</a></li>
    </ul>
  </nav>
</header>
```

Notez le **bouton burger** (`.nav-toggle`) : invisible sur ordinateur, il
apparaîtra sur mobile. On y reviendra en partie 2.

### b) La mise en forme (CSS)

On utilise **Flexbox** pour aligner logo et liens, et `position: sticky` pour
que la barre reste visible au défilement.

```css
.site-header {
  position: sticky;   /* la barre colle en haut… */
  top: 0;             /* …à 0px du bord supérieur */
  background: #ffffff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  z-index: 100;       /* passe au-dessus du contenu */
}

.navbar {
  max-width: 1100px;
  margin: 0 auto;                 /* centre la barre */
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between; /* logo à gauche, liens à droite */
}

.nav-logo {
  font-weight: 700;
  font-size: 1.25rem;
  text-decoration: none;
  color: #17132a;
}

.nav-links {
  list-style: none;   /* enlève les puces */
  display: flex;
  gap: 1.5rem;
  margin: 0;
  padding: 0;
}

.nav-links a {
  text-decoration: none;
  color: #17132a;
  transition: color 0.2s;
}

.nav-links a:hover {
  color: #5b3df0;     /* votre couleur d'accent */
}

/* Le lien "Contact" mis en avant comme un bouton */
.nav-cta {
  background: #5b3df0;
  color: #fff !important;
  padding: 0.5rem 1rem;
  border-radius: 8px;
}
```

### c) Le défilement doux (smooth scroll)

Par défaut, cliquer sur une ancre **saute** brutalement. Une seule ligne rend
le défilement fluide :

```css
html {
  scroll-behavior: smooth;
}
```

⚠️ Comme la navbar est **collante**, elle recouvre le haut des sections quand on
y saute. On corrige avec `scroll-margin-top` sur les sections :

```css
section {
  scroll-margin-top: 80px;  /* ≈ hauteur de la navbar */
}
```

> 🖼️ **Capture à ajouter** : la navbar sur ordinateur (liens visibles) et sur
> mobile (burger).

---

## 2. La navbar responsive : le menu burger 🍔

Sur un téléphone, les liens ne tiennent plus en largeur. La solution standard :
les **cacher derrière une icône « burger »** (☰) qui déploie le menu au clic.

### a) Le CSS : basculer selon la taille d'écran

On masque le burger sur grand écran, et on inverse sur petit écran avec une
**media query** :

```css
/* Sur ordinateur : le burger est caché */
.nav-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

/* Sur mobile (≤ 768px) */
@media (max-width: 768px) {
  .nav-toggle {
    display: block;          /* le burger apparaît */
  }

  .nav-links {
    display: none;           /* les liens sont cachés… */
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    flex-direction: column;  /* …et empilés à la verticale */
    background: #fff;
    padding: 1rem 1.5rem;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  }

  .nav-links.open {
    display: flex;           /* …jusqu'à ce qu'on ouvre le menu */
  }
}
```

### b) Le JavaScript : ouvrir / fermer

Un petit script bascule la classe `.open` sur le menu quand on clique le
burger. Placez-le dans `js/script.js` :

```javascript
const toggle = document.querySelector('.nav-toggle');
const menu = document.querySelector('.nav-links');

toggle.addEventListener('click', () => {
  const isOpen = menu.classList.toggle('open');
  toggle.setAttribute('aria-expanded', isOpen);
});

// Confort : refermer le menu après avoir cliqué un lien (sur mobile)
menu.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    menu.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
  });
});
```

### c) L'accessibilité — ne pas l'oublier

Le bouton porte déjà les bons attributs dans notre HTML :

- `aria-label="Ouvrir le menu"` : décrit le bouton (l'icône ☰ ne dit rien à un
  lecteur d'écran) ;
- `aria-expanded="false"` : indique si le menu est ouvert — mis à jour par le
  JS ;
- `aria-controls="nav-menu"` : relie le bouton au menu qu'il contrôle.

> 💡 Un menu burger **sans JavaScript accessible**, c'est un menu qu'une partie
> de vos visiteurs ne pourra pas utiliser. Les trois attributs ci-dessus
> suffisent pour bien faire.

---

## 3. Les menus déroulants (dropdown) ▾

Quand une rubrique a des **sous-rubriques** (ex. « Services ▾ » → Photo,
Vidéo, Retouche), on utilise un menu déroulant.

### a) La structure HTML

Un élément de menu qui **contient** un sous-menu :

```html
<li class="dropdown">
  <a href="#services">Services ▾</a>
  <ul class="dropdown-menu">
    <li><a href="#photo">Photo</a></li>
    <li><a href="#video">Vidéo</a></li>
    <li><a href="#retouche">Retouche</a></li>
  </ul>
</li>
```

### b) L'affichage au survol (CSS pur)

La version la plus simple : le sous-menu est caché, et apparaît au **survol** du
parent. On positionne le sous-menu **par rapport** au parent.

```css
.dropdown {
  position: relative;         /* repère pour le sous-menu */
}

.dropdown-menu {
  list-style: none;
  margin: 0;
  padding: 0.5rem 0;
  position: absolute;
  top: 100%;                  /* juste sous le parent */
  left: 0;
  min-width: 160px;
  background: #fff;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
  border-radius: 8px;
  display: none;              /* caché par défaut */
}

.dropdown:hover .dropdown-menu {
  display: block;             /* visible au survol du parent */
}

.dropdown-menu a {
  display: block;
  padding: 0.5rem 1rem;
}
```

> 💡 **Survol ou clic ?** Le survol (`:hover`) est simple mais **ne marche pas
> au doigt** sur mobile. Pour un vrai site, on double souvent d'une **version au
> clic** en JavaScript (même principe que le burger : `classList.toggle` sur le
> sous-menu), et on gère le **clavier** (ouvrir avec Entrée, fermer avec
> Échap). Pour un site vitrine simple, le survol suffit souvent — mais ayez le
> réflexe mobile en tête.

---

## 4. La barre latérale (sidebar)

La **sidebar** est un menu **vertical**, sur le côté. Sur un site vitrine simple,
elle est rare ; on la choisit quand :

- il y a **beaucoup de rubriques** (une doc, un tableau de bord),
- ou pour servir de **menu mobile** qui **glisse** depuis le bord (une
  alternative élégante au burger déroulant).

Voici une sidebar **« off-canvas »** : cachée hors de l'écran, elle glisse à
l'ouverture, avec un fond sombre (*overlay*) derrière.

### a) Le HTML

```html
<button class="sidebar-open" aria-label="Ouvrir le menu">☰</button>

<div class="overlay" hidden></div>

<aside class="sidebar" aria-label="Menu latéral">
  <button class="sidebar-close" aria-label="Fermer le menu">✕</button>
  <ul>
    <li><a href="#accueil">Accueil</a></li>
    <li><a href="#apropos">À propos</a></li>
    <li><a href="#services">Services</a></li>
    <li><a href="#contact">Contact</a></li>
  </ul>
</aside>
```

### b) Le CSS

```css
.sidebar {
  position: fixed;
  top: 0;
  right: 0;
  height: 100vh;
  width: 260px;
  background: #1b1633;
  color: #fff;
  padding: 2rem 1.5rem;
  transform: translateX(100%);   /* poussée hors de l'écran, à droite */
  transition: transform 0.3s ease;
  z-index: 200;
}

.sidebar.open {
  transform: translateX(0);      /* glisse à sa place */
}

.overlay {
  position: fixed;
  inset: 0;                       /* couvre tout l'écran */
  background: rgba(0, 0, 0, 0.5);
  z-index: 150;
}
```

### c) Le JavaScript

```javascript
const sidebar = document.querySelector('.sidebar');
const overlay = document.querySelector('.overlay');
const openBtn = document.querySelector('.sidebar-open');
const closeBtn = document.querySelector('.sidebar-close');

function openSidebar() {
  sidebar.classList.add('open');
  overlay.hidden = false;
}
function closeSidebar() {
  sidebar.classList.remove('open');
  overlay.hidden = true;
}

openBtn.addEventListener('click', openSidebar);
closeBtn.addEventListener('click', closeSidebar);
overlay.addEventListener('click', closeSidebar);  // clic à côté = ferme
```

> 💡 **Navbar + burger** ou **sidebar** ? Les deux résolvent le menu mobile.
> Le burger déroule vers le bas (le plus courant sur un site vitrine) ; la
> sidebar glisse depuis le côté (plus adapté aux menus longs). Choisissez-en
> **un** et tenez-vous-y.

---

## ✅ Récapitulatif

Vous devez pouvoir :

- [ ] coder une **navbar** en Flexbox, **collante** (`sticky`) ;
- [ ] activer le **défilement doux** + corriger le décalage avec
      `scroll-margin-top` ;
- [ ] afficher un **menu burger** sur mobile via une **media query** + un
      **toggle JS** ;
- [ ] renseigner les attributs **`aria-*`** du bouton burger ;
- [ ] créer un **dropdown** au survol (et savoir qu'une version au clic est
      nécessaire sur mobile) ;
- [ ] faire glisser une **sidebar off-canvas** avec overlay.

Votre site se parcourt maintenant du bureau au téléphone. 🎉

---

## 🧭 Prochaine étape

Le visiteur est arrivé et sait naviguer : accueillons-le avec un **hero** qui
donne envie de rester. 👉
""",
        )

        # ============================================================== #
        # COMPOSANTS DE CONTENU
        # ============================================================== #
        self._theory(
            chapter, 7,
            "La section hero",
            "site-vitrine-hero",
            duration=35,
            points=15,
            content="""# La section « hero » 🦸

Le **hero** est le grand bloc qu'on voit en arrivant sur le site, juste sous la
navbar. C'est votre **première impression** : en une seconde, le visiteur doit
comprendre qui vous êtes et avoir envie de rester. On le soigne particulièrement.

## 🎯 Objectifs

À la fin de cette leçon, vous saurez :

- ✅ identifier les **ingrédients** d'un bon hero
- ✅ le **coder** : titre, accroche, bouton d'action, image de fond
- ✅ garder le texte **lisible** sur une image (technique de l'overlay)
- ✅ connaître les **variantes** et éviter les **erreurs classiques**

---

## 1. Les ingrédients d'un bon hero

Un hero efficace tient en quatre éléments, pas plus :

- un **titre** fort (`<h1>`) — qui vous êtes / ce que vous proposez ;
- une **phrase d'accroche** courte (`<p>`) ;
- un **bouton d'action** (« call-to-action » : *Me contacter*, *Voir mes
  projets*…) — un simple lien `<a>` vers une section ;
- souvent une **image** ou une **couleur de fond**.

> 💡 Le hero répond à la question muette du visiteur : *« Je suis au bon
> endroit ? »* Un titre vague comme *« Bienvenue »* la laisse sans réponse.

---

## 2. Construire le hero

On remplit la section `#accueil` préparée dans l'ossature.

### a) Le HTML

```html
<section id="accueil" class="hero">
  <div class="hero-content">
    <h1>Studio Lumière</h1>
    <p>Photographe indépendant — je capture vos plus beaux moments.</p>
    <a href="#contact" class="btn btn-primary">Me contacter</a>
  </div>
</section>
```

Le `<div class="hero-content">` regroupe le texte pour le centrer et limiter sa
largeur.

### b) Le CSS : image de fond + centrage

```css
.hero {
  min-height: 90vh;              /* presque toute la hauteur de l'écran */
  display: flex;                 /* centrage… */
  align-items: center;           /* …vertical */
  justify-content: center;       /* …horizontal */
  text-align: center;
  padding: 2rem;
  color: #fff;

  /* L'astuce clé : un voile sombre PAR-DESSUS l'image, pour la lisibilité */
  background-image:
    linear-gradient(rgba(0, 0, 0, 0.45), rgba(0, 0, 0, 0.45)),
    url("../assets/images/hero.jpg");
  background-size: cover;        /* l'image couvre toute la zone */
  background-position: center;
}

.hero-content {
  max-width: 640px;             /* le texte ne s'étale pas trop */
}

.hero h1 {
  font-size: clamp(2rem, 5vw, 3.5rem);  /* s'adapte à l'écran */
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.25rem;
  margin-bottom: 2rem;
}
```

### c) Le bouton d'action (réutilisable)

On crée un style de bouton **`.btn`** qu'on réutilisera partout (contact,
services…) :

```css
.btn {
  display: inline-block;
  text-decoration: none;
  padding: 0.85rem 1.75rem;
  border-radius: 8px;
  font-weight: 600;
  transition: transform 0.2s, background 0.2s;
}

.btn-primary {
  background: #5b3df0;
  color: #fff;
}

.btn-primary:hover {
  background: #4527d6;
  transform: translateY(-2px);   /* léger soulèvement au survol */
}
```

### Les deux techniques à retenir

- **L'overlay** : le double `linear-gradient(...) , url(...)` superpose un voile
  sombre translucide sur l'image. Sans lui, un texte blanc devient illisible sur
  les zones claires de la photo.
- **`clamp()`** : `clamp(2rem, 5vw, 3.5rem)` donne un titre qui **grandit avec
  l'écran** mais reste borné — responsive sans media query.

> 🖼️ **Capture à ajouter** : trois exemples de hero (photo plein écran, dégradé,
> texte + image côte à côte).

---

## 3. Quelques variantes

Le hero ne se limite pas à une photo plein écran :

- **Dégradé de couleur** (sans image) : remplacez le `background-image` par
  `background: linear-gradient(135deg, #5b3df0, #8471f5);`. Sobre et léger.
- **Hero « scindé »** (*split*) : le texte à gauche, une image à droite, avec un
  affichage en deux colonnes (Flexbox ou Grid) qui **s'empile** sur mobile.
- **Avec une accroche secondaire** : un petit texte au-dessus du titre (« Basé à
  Lyon · Disponible ») pour situer d'emblée.

---

## 4. Les erreurs classiques à éviter

- ❌ **Titre vague** (« Bienvenue sur mon site ») : dites *qui* et *quoi*.
- ❌ **Trop de texte** : le hero accroche, il ne raconte pas tout — c'est le
  rôle des sections suivantes.
- ❌ **Contraste insuffisant** : texte clair sur image claire = illisible.
  L'overlay règle ça.
- ❌ **Bouton fantôme** : le call-to-action doit **sauter aux yeux** (couleur
  d'accent, taille suffisante).
- ❌ **Image trop lourde** : une photo de 8 Mo ralentit le premier affichage.
  On compressera au chapitre Finitions.

---

## ✅ Récapitulatif

Vous devez pouvoir :

- [ ] citer les **4 ingrédients** d'un hero ;
- [ ] coder un hero **centré** (Flexbox) sur toute la hauteur ;
- [ ] poser une **image de fond** avec **overlay** pour la lisibilité ;
- [ ] rendre le titre **fluide** avec `clamp()` ;
- [ ] créer un **bouton `.btn` réutilisable** ;
- [ ] éviter les erreurs classiques (titre vague, contraste, bouton discret).

Votre visiteur est accroché. Racontons-lui maintenant qui vous êtes. 🎯

---

## 🧭 Prochaine étape

On structure les sections de **présentation** : « à propos » et « services » en
cartes. 👉
""",
        )

        self._theory(
            chapter, 8,
            "Structurer une page de présentation (à propos / services)",
            "site-vitrine-presentation",
            duration=35,
            points=15,
            content="""# Structurer une page de présentation 📄

Après le hero viennent les sections qui **expliquent** : qui vous êtes (« à
propos ») et ce que vous proposez (« services »). On y introduit deux motifs de
mise en page qu'on retrouve partout sur le web : le **duo texte + image** et la
**grille de cartes**.

## 🎯 Objectifs

À la fin de cette leçon, vous saurez :

- ✅ structurer une section **« À propos »** (texte + image côte à côte)
- ✅ créer une **carte** réutilisable et l'afficher en **grille responsive**
- ✅ **rythmer** la page pour qu'elle respire

---

## 1. Un conteneur commun à toutes les sections

Nos sections partagent la même largeur maximale et les mêmes marges. On crée un
**`.container`** réutilisable pour ne pas se répéter :

```css
.container {
  max-width: 1100px;
  margin: 0 auto;        /* centre le contenu */
  padding: 4rem 1.5rem;  /* de l'air en haut/bas, des marges sur les côtés */
}

/* Un titre de section cohérent partout */
.section-title {
  font-size: 2rem;
  text-align: center;
  margin-bottom: 2.5rem;
}
```

---

## 2. La section « À propos » (texte + image)

Le motif classique : le **texte d'un côté**, une **image de l'autre**, qui
**s'empilent** sur mobile.

### a) Le HTML

```html
<section id="apropos" class="about">
  <div class="container about-grid">
    <div class="about-text">
      <h2 class="section-title">À propos</h2>
      <p>
        Photographe passionné depuis dix ans, je transforme les instants du
        quotidien en souvenirs intemporels. Basé à Lyon, je me déplace partout
        en France.
      </p>
    </div>
    <img src="assets/images/portrait.jpg" alt="Portrait du photographe">
  </div>
</section>
```

### b) Le CSS (avec CSS Grid)

```css
.about-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;  /* deux colonnes égales */
  gap: 3rem;
  align-items: center;
}

.about-grid img {
  width: 100%;
  border-radius: 12px;
}

/* Sur mobile : une seule colonne, les blocs s'empilent */
@media (max-width: 768px) {
  .about-grid {
    grid-template-columns: 1fr;
  }
}
```

> 💡 `1fr 1fr` = deux colonnes qui se **partagent l'espace** à parts égales. Le
> `fr` (« fraction ») est l'unité reine de CSS Grid.

---

## 3. Les services en cartes 🃏

Pour présenter plusieurs offres, le motif universel est la **grille de cartes** :
chacune avec une **icône**, un **titre** et une **courte description**.

### a) Le HTML

On utilise `<article>` : chaque carte est un contenu **autonome** (rappel de la
leçon sémantique).

```html
<section id="services" class="services">
  <div class="container">
    <h2 class="section-title">Mes services</h2>

    <div class="cards">
      <article class="card">
        <div class="card-icon">📷</div>
        <h3>Portrait</h3>
        <p>Des séances en studio ou en extérieur, à votre image.</p>
      </article>

      <article class="card">
        <div class="card-icon">💍</div>
        <h3>Mariage</h3>
        <p>Je raconte votre grand jour, de la préparation à la fête.</p>
      </article>

      <article class="card">
        <div class="card-icon">🏢</div>
        <h3>Entreprise</h3>
        <p>Photos corporate, événements et portraits d'équipe.</p>
      </article>
    </div>
  </div>
</section>
```

### b) La grille responsive — sans media query !

Voici l'un des plus beaux tours de CSS Grid : la grille s'adapte **toute seule**
au nombre de colonnes que l'écran peut accueillir.

```css
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
}
```

Décryptage de `repeat(auto-fit, minmax(220px, 1fr))` :

- chaque carte fait **au minimum 220px**, et **au plus** une fraction égale de
  l'espace ;
- `auto-fit` place **autant de colonnes que possible** : 3 sur un large écran,
  2 sur une tablette, 1 sur un téléphone — **automatiquement**.

### c) Le style de la carte (réutilisable)

```css
.card {
  background: #fff;
  border: 1px solid #e3e0f0;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-4px);              /* la carte se soulève */
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}

.card-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}
```

> 💡 La **carte** est un composant qu'on retrouvera pour la galerie, le
> portfolio, les témoignages… Voyez-la comme une brique réutilisable : même
> style, contenu variable.

---

## 4. Rythmer la page pour qu'elle respire

Une page de sections identiques fatigue l'œil. Trois réflexes :

- **Alterner les fonds** : une section sur deux avec un fond légèrement teinté,
  pour marquer la séparation.

```css
.about {
  background: #f6f5fb;   /* fond doux */
}
.services {
  background: #ffffff;   /* fond blanc */
}
```

- **Des espacements réguliers** : le `padding: 4rem 1.5rem` du `.container`
  donne le même rythme vertical partout.
- **Des titres de section cohérents** : la classe `.section-title` assure la
  même taille et le même alignement à chaque section.

> 🖼️ **Capture à ajouter** : la section « à propos » (texte + image) suivie de
> la rangée de 3 cartes de services.

---

## ✅ Récapitulatif

Vous devez pouvoir :

- [ ] créer un **`.container`** commun (largeur max + marges) ;
- [ ] disposer **texte + image côte à côte** en CSS Grid, empilés sur mobile ;
- [ ] construire une **carte** réutilisable (`<article>` + style + survol) ;
- [ ] afficher les cartes en **grille responsive** avec
      `repeat(auto-fit, minmax(...))` ;
- [ ] **rythmer** la page (fonds alternés, espacements, titres cohérents).

Votre visiteur sait maintenant qui vous êtes et ce que vous offrez. Montrons-lui
vos réalisations. 🎯

---

## 🧭 Prochaine étape

Place aux images qui parlent : **galerie, portfolio & témoignages**. 👉
""",
        )

        self._theory(
            chapter, 9,
            "Galerie, portfolio & témoignages",
            "site-vitrine-galerie",
            duration=35,
            points=15,
            content="""# Galerie, portfolio & témoignages 🖼️

Ces sections **montrent** plutôt qu'elles ne racontent : elles exposent vos
réalisations et apportent la **preuve sociale** qui rassure. Trois motifs à
maîtriser : la **galerie d'images**, le **portfolio** de projets, et les
**témoignages**.

## 🎯 Objectifs

À la fin de cette leçon, vous saurez :

- ✅ construire une **galerie d'images** responsive et bien cadrée
- ✅ présenter un **portfolio** de réalisations (cartes projet)
- ✅ afficher des **témoignages** avec des balises sémantiques

---

## 1. La galerie d'images

### a) Le HTML

```html
<section id="galerie" class="gallery">
  <div class="container">
    <h2 class="section-title">Galerie</h2>
    <div class="gallery-grid">
      <img src="assets/images/photo-1.jpg" alt="Séance portrait en extérieur">
      <img src="assets/images/photo-2.jpg" alt="Cérémonie de mariage">
      <img src="assets/images/photo-3.jpg" alt="Portrait d'équipe en entreprise">
      <img src="assets/images/photo-4.jpg" alt="Détail d'une alliance">
    </div>
  </div>
</section>
```

> ♿ Chaque image porte un **`alt` descriptif** : c'est ce que « lit » un lecteur
> d'écran, et ce que Google indexe. Jamais d'`alt` vide sur une image de
> contenu.

### b) Le CSS : une grille bien cadrée

```css
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
}

.gallery-grid img {
  width: 100%;
  height: 220px;
  object-fit: cover;        /* remplit le cadre SANS déformer l'image */
  border-radius: 8px;
  transition: transform 0.3s;
}

.gallery-grid img:hover {
  transform: scale(1.03);   /* léger zoom au survol */
}
```

Deux points clés :

- **`object-fit: cover`** : vos photos n'ont pas toutes le même format. Cette
  règle les fait **remplir** un cadre fixe en **rognant** proprement, plutôt que
  de les étirer. Indispensable pour une galerie régulière.
- **`auto-fill`** vs `auto-fit` : `auto-fill` **garde** les colonnes vides à
  droite (les images restent à leur taille) ; `auto-fit` les **étire** pour
  occuper toute la largeur. Testez les deux, choisissez selon le rendu voulu.

### c) Agrandir au clic : la « lightbox »

Cliquer sur une vignette pour l'afficher en grand s'appelle une **lightbox**.
Une version minimale en JavaScript : on affiche l'image cliquée dans une
sur-couche.

```javascript
const images = document.querySelectorAll('.gallery-grid img');
const lightbox = document.querySelector('.lightbox');
const lightboxImg = document.querySelector('.lightbox img');

images.forEach((img) => {
  img.addEventListener('click', () => {
    lightboxImg.src = img.src;
    lightbox.classList.add('open');
  });
});

lightbox.addEventListener('click', () => lightbox.classList.remove('open'));
```

> 💡 Pour aller plus loin sans réinventer la roue, des petites bibliothèques
> gratuites (ex. **GLightbox**) font ça très bien. Mais coder la version simple
> vous fait comprendre le principe.

---

## 2. Le portfolio : des cartes projet

Un portfolio est une galerie **enrichie** : chaque réalisation a un **titre** et
souvent un **lien**. On réutilise notre composant **carte**.

```html
<div class="cards">
  <article class="project-card">
    <img src="assets/images/projet-1.jpg" alt="Aperçu du projet Mariage Julie & Tom">
    <div class="project-body">
      <h3>Mariage — Julie & Tom</h3>
      <p>Reportage complet, Lyon, 2024.</p>
      <a href="#" class="btn btn-primary">Voir le projet</a>
    </div>
  </article>
  <!-- …autres projets -->
</div>
```

```css
.project-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;                 /* l'image épouse les coins arrondis */
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
}

.project-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.project-body {
  padding: 1.25rem;
}
```

On profite de la grille `.cards` (vue à la leçon précédente) pour disposer les
projets de façon responsive.

> 💡 **Filtrage par catégorie** (Photo / Vidéo / Tous…) : c'est une évolution
> naturelle du portfolio, réalisée en JavaScript (afficher/masquer selon un
> attribut `data-categorie`). Optionnel pour un premier site.

---

## 3. Les témoignages

La **preuve sociale** rassure : voir que d'autres sont satisfaits lève les
hésitations. On utilise des balises **sémantiques** dédiées à la citation.

```html
<div class="testimonials">
  <figure class="testimonial">
    <blockquote>
      « Un travail magnifique, à l'écoute et vraiment professionnel. »
    </blockquote>
    <figcaption>
      <img src="assets/images/marie.jpg" alt="">
      <div>
        <strong>Marie D.</strong>
        <span>Mariée en 2024</span>
      </div>
    </figcaption>
  </figure>
  <!-- …autres témoignages -->
</div>
```

- `<blockquote>` : une **citation** — la balise dédiée.
- `<figure>` / `<figcaption>` : le témoignage et son **auteur**.
- L'`alt=""` **vide** sur la photo de profil est volontaire ici : l'image est
  purement décorative, le nom est déjà écrit juste à côté.

```css
.testimonials {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.testimonial {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 0;                        /* figure a une marge par défaut */
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
}

.testimonial blockquote {
  margin: 0 0 1rem;
  font-style: italic;
}

.testimonial figcaption {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.testimonial figcaption img {
  width: 48px;
  height: 48px;
  border-radius: 50%;               /* photo ronde */
  object-fit: cover;
}
```

> 🖼️ **Capture à ajouter** : une galerie d'images + une rangée de témoignages.

---

## ✅ Récapitulatif

Vous devez pouvoir :

- [ ] afficher une **galerie** en grille avec **`object-fit: cover`** ;
- [ ] mettre des **`alt` descriptifs** (et savoir quand l'`alt` est vide) ;
- [ ] comprendre la différence **`auto-fill` / `auto-fit`** ;
- [ ] connaître le principe d'une **lightbox** ;
- [ ] présenter un **portfolio** en cartes projet ;
- [ ] structurer un **témoignage** avec `figure` / `blockquote` / `figcaption`.

Vos réalisations sont mises en valeur et vous inspirez confiance. Il ne reste
qu'à permettre au visiteur de vous joindre. 🎯

---

## 🧭 Prochaine étape

Le composant le plus utile d'un site vitrine : la **page de contact** avec un
formulaire qui **envoie vraiment** un e-mail, sans serveur. 👉
""",
        )

        self._theory(
            chapter, 10,
            "La page de contact (formulaire Formspree)",
            "site-vitrine-contact",
            duration=35,
            points=20,
            content="""# La page de contact ✉️

Un site vitrine sert souvent à une chose : **être contacté**. Le défi ? Un
formulaire HTML ne fait, à lui seul, **rien** — il faut normalement un serveur
pour recevoir et envoyer les messages. On va contourner ça avec **Formspree**,
qui joue ce rôle **gratuitement**, sans une ligne de backend.

## 🎯 Objectifs

À la fin de cette leçon, vous saurez :

- ✅ construire un **formulaire** HTML **accessible**
- ✅ le rendre **fonctionnel** avec **Formspree** (aucun serveur)
- ✅ styliser les champs proprement
- ✅ ajouter un bloc d'**informations de contact**
- ✅ limiter le **spam**

---

## 1. Le formulaire HTML

Un formulaire, c'est une balise `<form>` contenant des **champs**, chacun avec
son **`<label>`**.

```html
<section id="contact" class="contact">
  <div class="container contact-grid">

    <div class="contact-info">
      <h2 class="section-title">Me contacter</h2>
      <p>Un projet, une question ? Écrivez-moi, je réponds sous 48 h.</p>
      <ul class="contact-list">
        <li>📧 <a href="mailto:contact@studio-lumiere.fr">contact@studio-lumiere.fr</a></li>
        <li>📞 <a href="tel:+33612345678">06 12 34 56 78</a></li>
        <li>📍 Lyon, France</li>
      </ul>
    </div>

    <form class="contact-form" action="https://formspree.io/f/VOTRE_ID" method="POST">
      <div class="field">
        <label for="name">Votre nom</label>
        <input type="text" id="name" name="name" required>
      </div>

      <div class="field">
        <label for="email">Votre e-mail</label>
        <input type="email" id="email" name="email" required>
      </div>

      <div class="field">
        <label for="message">Votre message</label>
        <textarea id="message" name="message" rows="5" required></textarea>
      </div>

      <button type="submit" class="btn btn-primary">Envoyer</button>
    </form>

  </div>
</section>
```

Points importants :

- Chaque **`<label>`** est relié à son champ par `for="id"` ↔ `id="…"` : cliquer
  le libellé place le curseur dans le champ, et les lecteurs d'écran annoncent
  la bonne étiquette. **♿ Ne jamais faire de champ sans label.**
- **`type="email"`** : le navigateur **valide** l'adresse automatiquement.
- **`required`** : empêche l'envoi si le champ est vide.
- L'attribut **`name`** de chaque champ est le nom sous lequel vous recevrez la
  donnée — indispensable.

---

## 2. Le rendre fonctionnel avec Formspree

Formspree reçoit la soumission et vous la **transfère par e-mail**. Marche à
suivre :

1. Créez un compte gratuit sur **https://formspree.io/**.
2. Créez un **nouveau formulaire** (*New form*) et indiquez l'e-mail où recevoir
   les messages.
3. Formspree vous donne une **adresse d'envoi** du type
   `https://formspree.io/f/xxxxxx`.
4. Collez cette adresse dans l'attribut **`action`** de votre `<form>` (à la
   place de `VOTRE_ID`), avec **`method="POST"`**.
5. Publiez votre site, remplissez le formulaire et **envoyez** : le premier
   message vous demande de **confirmer** votre adresse (une seule fois). Ensuite,
   tout arrive dans votre boîte mail. 🎉

> ⚠️ Formspree fonctionne depuis un **site en ligne** (votre URL GitHub Pages),
> pas toujours depuis un simple fichier ouvert en local. Testez sur la version
> publiée.

### Options utiles

- **Rediriger après l'envoi** vers une page de remerciement :

```html
<input type="hidden" name="_next" value="https://votre-site.github.io/merci.html">
```

- **Personnaliser le sujet** de l'e-mail reçu :

```html
<input type="hidden" name="_subject" value="Nouveau message depuis le site">
```

---

## 3. Styliser le formulaire

```css
.contact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
}

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 1.25rem;
}

.field label {
  margin-bottom: 0.4rem;
  font-weight: 600;
}

.field input,
.field textarea {
  padding: 0.7rem;
  border: 1px solid #e3e0f0;
  border-radius: 8px;
  font: inherit;              /* même police que le reste du site */
}

.field input:focus,
.field textarea:focus {
  outline: 2px solid #5b3df0; /* focus bien visible (accessibilité) */
  border-color: #5b3df0;
}

.contact-list {
  list-style: none;
  padding: 0;
  line-height: 2;
}

@media (max-width: 768px) {
  .contact-grid {
    grid-template-columns: 1fr;  /* infos au-dessus, formulaire en dessous */
  }
}
```

> 🖼️ **Capture à ajouter** : le bloc d'infos et le formulaire côte à côte, avec
> un champ en focus.

---

## 4. Limiter le spam (astuce du « pot de miel »)

Les robots remplissent les formulaires automatiquement. Formspree filtre déjà
beaucoup, mais on peut ajouter un **champ piège** (*honeypot*) : invisible pour
un humain, mais qu'un robot remplira — Formspree ignore alors l'envoi.

```html
<input type="text" name="_gotcha" style="display:none">
```

> 💡 On ne met **pas** de `label` sur ce champ, et on le **cache** en CSS : un
> vrai visiteur ne le voit jamais.

---

## 5. Envie de bloc carte ?

Pour situer votre activité, vous pouvez intégrer une **carte** (Google Maps ou
OpenStreetMap) via un simple `<iframe>` fourni par le service (*Partager →
Intégrer une carte*). Optionnel, mais rassurant pour une activité locale.

---

## ✅ Récapitulatif

Vous devez pouvoir :

- [ ] construire un formulaire avec **`<label>` reliés** à leurs champs ;
- [ ] utiliser **`type="email"`** et **`required`** ;
- [ ] brancher **Formspree** via l'attribut **`action`** + `method="POST"` ;
- [ ] styliser les champs, avec un **focus visible** ;
- [ ] afficher un bloc d'**informations de contact** ;
- [ ] ajouter un **honeypot** anti-spam.

Votre visiteur peut désormais vous écrire, et vous recevez ses messages. 🎯

---

## 🧭 Prochaine étape

On termine la page par le bas : le **footer** et les **composants
réutilisables** (boutons, cartes) qui donnent au site sa cohérence. 👉
""",
        )

        self._theory(
            chapter, 11,
            "Le footer & les composants réutilisables",
            "site-vitrine-footer",
            duration=30,
            points=15,
            content="""# Le footer & les composants réutilisables 🧱

On termine la page par le bas : le **footer**. Et on en profite pour formaliser
les petites briques qu'on réutilise partout — **boutons** et **cartes** — car
c'est cette cohérence qui distingue un site pro d'un site bricolé.

## 🎯 Objectifs

À la fin de cette leçon, vous saurez :

- ✅ construire un **footer** complet (liens, réseaux, mentions)
- ✅ standardiser vos **boutons** (variantes + états)
- ✅ penser vos composants comme un mini **système de design**

---

## 1. Le footer

Le footer regroupe en général : un rappel du **logo**, des **liens** de
navigation, les **réseaux sociaux**, le **copyright** et les **liens légaux**.

### a) Le HTML

```html
<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      <h3 class="footer-logo">Studio Lumière</h3>
      <p>Photographe indépendant, basé à Lyon.</p>
    </div>

    <nav aria-label="Liens de bas de page">
      <h4>Navigation</h4>
      <ul>
        <li><a href="#apropos">À propos</a></li>
        <li><a href="#services">Services</a></li>
        <li><a href="#galerie">Galerie</a></li>
        <li><a href="#contact">Contact</a></li>
      </ul>
    </nav>

    <div class="footer-social">
      <h4>Suivez-moi</h4>
      <a href="https://instagram.com/…" aria-label="Instagram">📷</a>
      <a href="https://facebook.com/…" aria-label="Facebook">👍</a>
    </div>
  </div>

  <div class="footer-bottom">
    <p>© 2026 Studio Lumière. Tous droits réservés.</p>
    <p>
      <a href="mentions-legales.html">Mentions légales</a> ·
      <a href="confidentialite.html">Confidentialité</a>
    </p>
  </div>
</footer>
```

> ♿ Les liens réseaux ne contiennent qu'une **icône** : sans texte, on ajoute un
> **`aria-label`** pour qu'un lecteur d'écran annonce « Instagram », « Facebook ».

> ⚖️ **Les liens légaux ne sont pas décoratifs.** En France, même un site
> vitrine doit afficher des **mentions légales** (identité de l'éditeur,
> hébergeur). Prévoyez ces pages — vous savez déjà les structurer.

### b) Le CSS

```css
.site-footer {
  background: #17132a;
  color: #cbc7dd;
  padding-top: 3rem;
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 2rem;
}

.site-footer a {
  color: #cbc7dd;
  text-decoration: none;
}
.site-footer a:hover {
  color: #ffffff;
}

.site-footer ul {
  list-style: none;
  padding: 0;
  line-height: 2;
}

.footer-social a {
  font-size: 1.5rem;
  margin-right: 0.75rem;
}

.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 2rem;
  padding: 1.5rem;
  text-align: center;
  font-size: 0.9rem;
}
```

> 💡 **Vraies icônes** : les emojis dépannent, mais une bibliothèque comme
> **Font Awesome** ou **Lucide** offre de vraies icônes de réseaux, nettes et
> homogènes. On les branche avec un `<link>` (Font Awesome) ou un `<svg>`.

---

## 2. Standardiser ses boutons

Vous avez créé `.btn` / `.btn-primary` pour le hero. Formalisons une petite
**famille** de boutons, réutilisable partout.

```css
/* La base commune à tous les boutons */
.btn {
  display: inline-block;
  text-decoration: none;
  padding: 0.85rem 1.75rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: 2px solid transparent;
  transition: transform 0.2s, background 0.2s, color 0.2s;
}

/* Variante pleine (action principale) */
.btn-primary {
  background: #5b3df0;
  color: #fff;
}
.btn-primary:hover {
  background: #4527d6;
  transform: translateY(-2px);
}

/* Variante contour (action secondaire) */
.btn-outline {
  background: transparent;
  color: #5b3df0;
  border-color: #5b3df0;
}
.btn-outline:hover {
  background: #5b3df0;
  color: #fff;
}

/* Focus clavier visible — accessibilité */
.btn:focus-visible {
  outline: 3px solid rgba(91, 61, 240, 0.4);
  outline-offset: 2px;
}
```

> 💡 Le principe : **une base `.btn`** (forme, espacement, transition) + des
> **variantes** (`-primary`, `-outline`) qui ne changent que les couleurs. On
> écrit le style **une fois**, on l'utilise **partout**.

---

## 3. Penser « système de design »

Sans le savoir, vous avez déjà construit un petit **système de design** : un jeu
de composants cohérents que vous réutilisez sur tout le site.

| Composant | Classe | Où on le réutilise |
|---|---|---|
| Conteneur centré | `.container` | Toutes les sections |
| Titre de section | `.section-title` | À propos, services, galerie… |
| Bouton | `.btn` + variantes | Hero, services, contact |
| Carte | `.card` | Services, portfolio |

> 💡 **La cohérence, c'est le secret d'un site qui fait pro.** Mêmes marges,
> mêmes rayons de coin, mêmes couleurs, mêmes boutons partout. Réutiliser vos
> classes plutôt que réinventer à chaque section vous y oblige naturellement.

> 🖼️ **Capture à ajouter** : un footer type + un aperçu des boutons (plein et
> contour).

---

## ✅ Récapitulatif

Vous devez pouvoir :

- [ ] construire un **footer** en grille (logo, liens, réseaux, bas de page) ;
- [ ] rendre les **icônes-liens accessibles** avec `aria-label` ;
- [ ] prévoir les **liens légaux** (obligatoires) ;
- [ ] créer une **famille de boutons** (`.btn` + variantes + focus visible) ;
- [ ] réutiliser vos composants pour un rendu **cohérent** partout.

Le site est complet, du haut jusqu'en bas, et visuellement homogène. Il ne reste
qu'à le peaufiner. 🎯

---

## 🧭 Prochaine étape

Les **finitions** qui font la différence : responsive, SEO, accessibilité et
performance. 👉
""",
        )

        # ============================================================== #
        # FINITIONS & MISE EN LIGNE
        # ============================================================== #
        self._theory(
            chapter, 12,
            "Responsive & finitions : SEO, accessibilité, performance",
            "site-vitrine-finitions",
            duration=35,
            points=15,
            content="""# Responsive & finitions ✨

Votre site fonctionne. Il s'agit maintenant de le transformer en site
**soigné** : impeccable sur tous les écrans, bien référencé, accessible à tous
et rapide. Ce sont ces finitions, souvent négligées, qui font la différence.

## 🎯 Objectifs

À la fin de cette leçon, vous saurez :

- ✅ **vérifier le responsive** de chaque composant
- ✅ soigner le **référencement (SEO)**
- ✅ rendre le site **accessible**
- ✅ améliorer les **performances**
- ✅ **auditer** votre site avec Lighthouse

---

## 1. Responsive : le tour de contrôle

Vous avez travaillé **mobile-first** tout au long du chapitre. L'heure est à la
**vérification** : ouvrez les **DevTools** (`F12`) → **mode appareil**
(`Ctrl+Shift+M`) et parcourez votre site à la taille d'un téléphone.

Passez chaque composant en revue :

- [ ] la **navbar** bascule bien en **menu burger** ;
- [ ] les **grilles** (services, galerie) se **réempilent** en une colonne ;
- [ ] le **hero** reste lisible, le titre ne déborde pas ;
- [ ] le **formulaire** prend toute la largeur ;
- [ ] aucune **barre de défilement horizontale** ne traîne.

Rappel du levier de base — la **media query** :

```css
@media (max-width: 768px) {
  /* styles appliqués uniquement en dessous de 768px de large */
}
```

> ⚠️ Vérifiez que la balise **`<meta name="viewport">`** est bien présente dans
> le `<head>` : sans elle, le mobile affiche une version « dézoomée » illisible.

---

## 2. Le référencement (SEO) de base

Le SEO aide Google à **comprendre et classer** votre site. Trois réglages
essentiels, dans le `<head>` :

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- Titre unique et descriptif (onglet + résultat Google) -->
  <title>Studio Lumière — Photographe à Lyon</title>

  <!-- Description affichée sous le titre dans Google (≤ 160 caractères) -->
  <meta name="description" content="Photographe indépendant à Lyon : portraits, mariages, entreprise. Réservez votre séance.">

  <!-- Aperçu lors d'un partage sur les réseaux sociaux (Open Graph) -->
  <meta property="og:title" content="Studio Lumière — Photographe à Lyon">
  <meta property="og:description" content="Portraits, mariages et photographie d'entreprise.">
  <meta property="og:image" content="https://votre-site.github.io/assets/images/apercu.jpg">
  <meta property="og:type" content="website">

  <!-- Favicon : la petite icône de l'onglet -->
  <link rel="icon" href="assets/images/favicon.png">

  <link rel="stylesheet" href="css/style.css">
</head>
```

- Le **`<title>`** doit être **unique** et parlant : c'est le lien bleu dans
  Google.
- La **`description`** donne envie de cliquer.
- Les balises **Open Graph** (`og:*`) génèrent un **bel aperçu** quand on partage
  le lien sur les réseaux (image + titre au lieu d'une URL nue).
- Le HTML **sémantique** de la leçon 4.4 fait déjà une grande partie du travail.

---

## 3. L'accessibilité

Un site accessible est utilisable par **tout le monde**, y compris les personnes
en situation de handicap. La bonne nouvelle : vous avez déjà appliqué
l'essentiel. Vérifiez :

- [ ] **`alt`** sur toutes les images de contenu ;
- [ ] **contraste** suffisant texte/fond (un gris clair sur blanc ne passe pas) ;
- [ ] **navigation au clavier** : parcourez le site avec la touche `Tab`, chaque
      élément interactif doit être atteignable et son **focus visible**
      (`:focus-visible`) ;
- [ ] **hiérarchie des titres** : un seul `<h1>`, pas de saut de niveau ;
- [ ] **`<label>`** sur chaque champ de formulaire ;
- [ ] **`aria-label`** sur les boutons/liens porteurs d'une seule icône.

> 💡 Pour vérifier les **contrastes**, utilisez un outil comme *WebAIM Contrast
> Checker* : il vous dit si un couple de couleurs respecte les normes (WCAG AA).

---

## 4. La performance

Un site lent fait fuir. Sur un site vitrine, le principal coupable, ce sont les
**images**.

- **Compressez** vos images avant de les mettre en ligne : *TinyPNG* ou
  *Squoosh* réduisent le poids de 70 % sans perte visible.
- **Redimensionnez** à la bonne taille : inutile de charger une photo de
  4000 px pour l'afficher dans une vignette de 300 px.
- Préférez le format **WebP** (plus léger que JPG/PNG).
- Activez le **chargement différé** des images hors écran :

```html
<img src="assets/images/photo.jpg" alt="…" loading="lazy">
```

`loading="lazy"` demande au navigateur de ne charger l'image que **lorsqu'on
approche d'elle** en défilant — la page s'affiche plus vite.

---

## 5. Auditer son site avec Lighthouse 🔦

Chrome intègre un outil qui **note** votre site sur 100 en Performance, SEO,
Accessibilité et Bonnes pratiques.

1. Ouvrez votre site, puis les **DevTools** (`F12`).
2. Onglet **Lighthouse** → **Analyze page load**.
3. Lisez le rapport : il **liste les problèmes** et **comment les corriger**.

> 💡 Visez le **vert** partout, mais ne devenez pas obsessionnel : un score de
> 90+ est déjà excellent pour un site vitrine. Lighthouse est surtout une
> **liste de courses** de finitions.

> 🖼️ **Capture à ajouter** : un rapport Lighthouse avec ses 4 scores.

---

## ✅ Récapitulatif

Vous devez pouvoir :

- [ ] **vérifier** chaque composant en **mode mobile** ;
- [ ] renseigner **`title`**, **`description`** et balises **Open Graph** ;
- [ ] ajouter un **favicon** ;
- [ ] valider l'**accessibilité** (alt, contraste, clavier, titres, labels) ;
- [ ] **compresser** et **différer** vos images (`loading="lazy"`) ;
- [ ] lancer un audit **Lighthouse** et lire son rapport.

Votre site est propre, rapide, partageable et accueillant pour tous. Reste la
consécration : le mettre en ligne. 🎯

---

## 🧭 Prochaine étape

La dernière ligne droite : **mettre votre site en ligne** et savoir le mettre à
jour. 👉
""",
        )

        self._theory(
            chapter, 13,
            "Mettre son site en ligne",
            "site-vitrine-mise-en-ligne",
            duration=30,
            points=15,
            content="""# Mettre son site en ligne 🌍

Le moment de vérité : rendre votre site accessible au monde entier. Vous avez
déjà publié une première version à la leçon Git ; ici, on **met en ligne la
version finale**, on découvre une **alternative**, et on voit comment brancher
un **vrai nom de domaine**.

## 🎯 Objectifs

À la fin de cette leçon, vous saurez :

- ✅ publier la version finale avec **GitHub Pages**
- ✅ déployer autrement avec **Netlify**
- ✅ **vérifier** votre site en ligne et déjouer les pièges classiques
- ✅ comprendre ce qu'est un **nom de domaine**
- ✅ **mettre à jour** votre site en une commande

---

## 1. Publier avec GitHub Pages (le fil rouge)

Vous connaissez déjà le principe (leçon 4.2). Pour publier la **version
finale**, il suffit d'envoyer votre dernier travail :

```bash
git add .
git commit -m "Version finale du site vitrine"
git push
```

Si GitHub Pages est déjà activé (*Settings → Pages*), votre site en ligne se met
à jour tout seul en une minute. Sinon, activez-le : branche **`main`**, dossier
**`/ (root)`**, **Save**.

Votre adresse est du type :

```text
https://<votre-pseudo>.github.io/mon-site-vitrine/
```

> 💡 Un changement n'apparaît pas ? Attendez une minute, puis forcez le
> rafraîchissement du navigateur (`Ctrl+Shift+R`) : votre navigateur garde
> parfois l'ancienne version en cache.

---

## 2. Alternative : Netlify (glisser-déposer)

**Netlify** est une autre plateforme d'hébergement gratuite, encore plus
immédiate pour un premier test :

1. Allez sur **https://app.netlify.com/drop**.
2. **Glissez-déposez** le dossier de votre site sur la page.
3. C'est en ligne, avec une URL aussitôt. 🪄

> 💡 Netlify peut aussi se **connecter à votre dépôt GitHub** : à chaque `push`,
> il redéploie automatiquement (comme GitHub Pages). Pratique quand le projet
> grandit.

**GitHub Pages ou Netlify ?** Les deux sont gratuits et excellents pour un site
statique. GitHub Pages garde tout au même endroit que votre code ; Netlify offre
le glisser-déposer et des options avancées. Choisissez celui qui vous parle.

---

## 3. Vérifier son site en ligne (et les pièges classiques)

Une fois en ligne, **testez pour de vrai** :

- ouvrez le site sur **votre téléphone** (pas seulement le mode mobile des
  DevTools) ;
- cliquez **tous les liens** du menu ;
- envoyez un message via le **formulaire** ;
- **partagez le lien** à un proche et regardez sur son écran.

Trois pièges qui « marchaient en local » mais cassent en ligne :

- 🔤 **La casse des noms de fichiers.** En ligne, `Photo.JPG` ≠ `photo.jpg`. Un
  lien `<img src="photo.jpg">` vers un fichier nommé `Photo.JPG` marche sur
  votre PC mais **casse en ligne**. D'où la règle du tout-minuscule.
- 📁 **Les chemins de fichiers.** Vérifiez que vos chemins sont **relatifs**
  (`assets/images/…`, `css/style.css`) et corrects.
- ✉️ **Le formulaire.** Formspree ne fonctionne **que depuis le site en ligne** :
  testez-le sur l'URL publiée, pas en local.

---

## 4. Un nom de domaine (notions)

L'adresse `https://pseudo.github.io/…` est parfaite pour commencer. Pour un
rendu plus professionnel, on peut acheter un **nom de domaine**
(`www.studio-lumiere.fr`).

- Un domaine s'**achète** chez un « registrar » (OVH, Gandi, Namecheap…), pour
  ~**10 €/an**.
- On le **relie** ensuite à GitHub Pages ou Netlify via leurs réglages
  (*Custom domain*).

> 💡 Ce n'est **pas nécessaire** pour valider ce chapitre : l'adresse
> `github.io` suffit largement. Le domaine personnalisé viendra si votre projet
> devient « sérieux ».

---

## 5. Mettre à jour son site : la boucle finale

À retenir pour toute la vie de votre site — publier une modification tient en
**trois commandes** :

```bash
git add .
git commit -m "Met à jour la galerie"
git push
```

Quelques secondes plus tard, votre site en ligne reflète le changement. C'est
tout. 🔁

---

## ✅ Récapitulatif

Vous devez pouvoir :

- [ ] publier la version finale via **GitHub Pages** (ou **Netlify**) ;
- [ ] **vérifier** votre site sur un vrai téléphone et partager le lien ;
- [ ] déjouer les pièges : **casse** des noms, **chemins**, **formulaire** en
      ligne ;
- [ ] savoir ce qu'est un **nom de domaine** et quand l'ajouter ;
- [ ] mettre à jour le site avec **add → commit → push**.

---

## 🎉 Bravo, vous y êtes !

Vous avez parcouru tout le chemin : de l'installation des outils jusqu'à un
**site vitrine en ligne**, en assemblant navigation, hero, présentation,
galerie, contact et footer. C'est une **vraie compétence**, et un premier projet
que vous pouvez montrer.

## 🧭 Prochaine étape

À vous de jouer pour de bon : place au **projet final**, où vous réaliserez
**votre propre** site vitrine. 🚀
""",
        )

        # ============================================================== #
        # PROJET FINAL (RÉDIGÉ)
        # ============================================================== #
        self._theory(
            chapter, 14,
            "Projet : réalise ton site vitrine",
            "site-vitrine-projet",
            duration=15,
            points=50,
            content="""# 🏆 Projet final : ton propre site vitrine

Le moment est venu de voler de vos propres ailes. Vous allez concevoir et
publier **votre** site vitrine, sur le thème de votre choix, en réutilisant les
composants du chapitre.

## Le sujet

Choisissez **un** thème qui vous parle :

- votre **portfolio** de développeur,
- une activité réelle ou fictive (**artisan, coach, restaurant, association**),
- un **produit** ou un **événement**.

## 📋 Cahier des charges (obligatoire)

Votre site doit assembler **au minimum** ces composants vus dans le chapitre :

- [ ] une **navigation** (navbar + ancres, responsive avec menu burger) ;
- [ ] une section **hero** avec titre, accroche et bouton d'action ;
- [ ] une section **à propos** ;
- [ ] une section **services / offres** (au moins 3 cartes) ;
- [ ] une **galerie** d'au moins 4 images ;
- [ ] un **formulaire de contact** fonctionnel (Formspree) ;
- [ ] un **footer** avec des liens de réseaux sociaux ;
- [ ] un affichage **responsive** (mobile + ordinateur).

## ✅ Critères d'évaluation (100 points)

| Critère | Points |
|---|---|
| Structure HTML sémantique et valide | 20 |
| Design cohérent, fidèle à une maquette | 20 |
| Responsive (mobile → grand écran) | 20 |
| Composants demandés présents et fonctionnels | 20 |
| Accessibilité & SEO de base | 10 |
| Site **publié en ligne** (URL fonctionnelle) | 10 |

## 📦 Ce qu'on attend en rendu

1. Le **lien du dépôt GitHub** (code source).
2. Le **lien du site en ligne** (GitHub Pages ou Netlify).
3. (Bonus) le lien de votre **maquette Figma**.

## 💡 Conseils

- Commencez **petit** : une seule page, bien faite, vaut mieux que dix
  inachevées.
- Assemblez les composants du chapitre comme des briques Lego.
- Faites **relire** votre site sur un téléphone.

---

Quand votre site est en ligne, partagez-le : c'est votre première vraie
réalisation web. 🚀
""",
        )

        # ============================================================== #
        # QUIZ DE VALIDATION (RÉDIGÉ)
        # ============================================================== #
        lesson_quiz = Lesson.objects.create(
            chapter=chapter,
            title="Quiz : valider le chapitre",
            slug="site-vitrine-quiz",
            lesson_type="QUIZ",
            order_index=15,
            estimated_duration=10,
            points=10,
            is_published=True,
            content="",
        )
        Quiz.objects.create(
            lesson=lesson_quiz,
            instructions="""# 📝 Quiz : le site vitrine de A à Z

Vérifiez que les composants et les étapes clés sont bien acquis.

**Score minimal** : 70 % · **Tentatives** : 3
""",
            passing_score=70,
            time_limit=10,
            max_attempts=3,
            randomize_questions=False,
            randomize_options=False,
            questions={
                "questions": [
                    {
                        "id": 1,
                        "question": "Sur mobile, comment affiche-t-on habituellement les liens d'une navbar qui ne tiennent plus en largeur ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "On les supprime"},
                            {"id": "b", "text": "Derrière une icône « burger » (☰) qui déploie le menu"},
                            {"id": "c", "text": "On réduit la taille du texte à 2px"},
                            {"id": "d", "text": "On met le site en paysage forcé"},
                        ],
                        "correct_answer": "b",
                        "points": 3,
                        "explanation": "Le menu burger cache les liens derrière une icône qu'on déploie au clic — le motif responsive standard.",
                    },
                    {
                        "id": 2,
                        "question": "Quel composant est la PREMIÈRE chose visible en arrivant sur un site vitrine ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "Le footer"},
                            {"id": "b", "text": "La section hero"},
                            {"id": "c", "text": "Le formulaire de contact"},
                            {"id": "d", "text": "La sidebar"},
                        ],
                        "correct_answer": "b",
                        "points": 2,
                        "explanation": "Le hero est le bloc d'accroche en haut de page : titre, phrase et bouton d'action.",
                    },
                    {
                        "id": 3,
                        "question": "Comment un site vitrine peut-il envoyer un e-mail depuis un formulaire SANS coder de serveur ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "Avec un service comme Formspree"},
                            {"id": "b", "text": "En installant PHP sur GitHub"},
                            {"id": "c", "text": "Ce n'est pas possible sans serveur"},
                            {"id": "d", "text": "Avec une balise <email>"},
                        ],
                        "correct_answer": "a",
                        "points": 3,
                        "explanation": "Formspree reçoit la soumission et la transfère par e-mail, sans backend à écrire.",
                    },
                    {
                        "id": 4,
                        "question": "À quoi sert GitHub Pages ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "À dessiner une maquette"},
                            {"id": "b", "text": "À héberger gratuitement un site statique"},
                            {"id": "c", "text": "À compresser des images"},
                            {"id": "d", "text": "À écrire du CSS plus vite"},
                        ],
                        "correct_answer": "b",
                        "points": 2,
                        "explanation": "GitHub Pages publie gratuitement le contenu d'un dépôt à une adresse <pseudo>.github.io.",
                    },
                    {
                        "id": 5,
                        "question": "Pour présenter 3 services côte à côte de façon responsive, quel motif est le plus adapté ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "Trois images de fond superposées"},
                            {"id": "b", "text": "Une grille de cartes (CSS Grid) qui se réempile sur mobile"},
                            {"id": "c", "text": "Un tableau HTML <table>"},
                            {"id": "d", "text": "Trois iframes"},
                        ],
                        "correct_answer": "b",
                        "points": 3,
                        "explanation": "La grille de cartes (CSS Grid) s'adapte : plusieurs colonnes sur grand écran, empilées sur mobile.",
                    },
                    {
                        "id": 6,
                        "question": "Quelle pratique améliore l'accessibilité ET le référencement des images ?",
                        "type": "multiple_choice",
                        "options": [
                            {"id": "a", "text": "Mettre les images en très haute résolution"},
                            {"id": "b", "text": "Renseigner l'attribut alt des images"},
                            {"id": "c", "text": "Nommer les fichiers avec des accents"},
                            {"id": "d", "text": "Utiliser uniquement des images de fond CSS"},
                        ],
                        "correct_answer": "b",
                        "points": 2,
                        "explanation": "L'attribut alt décrit l'image pour les lecteurs d'écran et les moteurs de recherche.",
                    },
                ]
            },
        )

        # ------------------------------------------------------------------ #
        lessons = chapter.lessons.count()
        remaining = [
            lesson.order_index
            for lesson in chapter.lessons.all()
            if "À rédiger" in (lesson.content or "")
        ]
        self.stdout.write(self.style.SUCCESS("\n✅ Section 4 chargée."))
        self.stdout.write(f"   Chapitre : {chapter.title} (order_index={chapter.order_index})")
        self.stdout.write(f"   Leçons   : {lessons} (théorie + 1 quiz, sans exercice bac à sable)")
        if remaining:
            self.stdout.write(
                self.style.WARNING(
                    "   ⚠️ Encore en squelette (« 🚧 À rédiger »), order_index : "
                    + ", ".join(str(i) for i in sorted(remaining))
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("   ✍️ Toutes les leçons sont rédigées."))
