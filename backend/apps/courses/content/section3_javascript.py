"""
Crée le chapitre 3 : Introduction à JavaScript, avec la même structure que
les chapitres HTML et CSS : une leçon théorique par thème, suivie d'un petit
exercice de mise en pratique immédiate, puis des exercices intégrateurs et
un quiz final.

Les exercices sur variables/conditions/boucles/fonctions/tableaux sont
réellement exécutés (assertions sur le comportement du code). Les exercices
sur le DOM/les événements vérifient la présence du bon code dans la source
(__source), faute de vrai navigateur dans le sandbox.

Usage: docker-compose exec backend python load_section_3_javascript.py
"""

from apps.courses.models import Chapter, Lesson, Exercise, Quiz


def upsert_theory(chapter, slug, title, order_index, content, duration, points):
    lesson, created = Lesson.objects.update_or_create(
        slug=slug,
        defaults={
            'chapter': chapter,
            'title': title,
            'lesson_type': 'THEORY',
            'order_index': order_index,
            'content': content,
            'video_url': '',
            'estimated_duration': duration,
            'points': points,
            'is_published': True,
        }
    )
    print(f"  {'✅ créée' if created else '♻️  mise à jour'} : {lesson.title}")
    return lesson


def upsert_exercise(chapter, slug, title, order_index, instructions,
                     starter_code, solution, tests, hints, duration=10, points=10,
                     difficulty='EASY', max_attempts=0, time_limit=600):
    lesson, created = Lesson.objects.update_or_create(
        slug=slug,
        defaults={
            'chapter': chapter,
            'title': title,
            'lesson_type': 'EXERCISE',
            'order_index': order_index,
            'content': '',
            'estimated_duration': duration,
            'points': points,
            'is_published': True,
        }
    )
    Exercise.objects.update_or_create(
        lesson=lesson,
        defaults={
            'instructions': instructions,
            'starter_code': starter_code,
            'solution': solution,
            'language': 'javascript',
            'tests': {'tests': tests},
            'difficulty': difficulty,
            'max_attempts': max_attempts,
            'time_limit': time_limit,
            'hints': hints,
        }
    )
    print(f"  {'✅ créée' if created else '♻️  mise à jour'} : {lesson.title}")
    return lesson


def build():
    """Construit ou met a jour ce bloc de contenu. Idempotent."""
    # ==========================================================================
    # CHAPITRE
    # ==========================================================================

    chapter, _ = Chapter.objects.update_or_create(
        slug='introduction-javascript',
        defaults={
            'title': 'Introduction à JavaScript',
            'description': """Donnez vie à vos pages web ! Après HTML (structure) et CSS (présentation),
        découvrez JavaScript, le langage qui rend une page interactive : variables, conditions,
        boucles, fonctions, tableaux, et une première approche du DOM et des événements.""",
            'order_index': 3,
            'estimated_duration': 60,
            'is_published': True,
        }
    )
    print(f"Chapitre : {chapter.title}\n")

    # ==========================================================================
    # 1. QU'EST-CE QUE JAVASCRIPT ?
    # ==========================================================================

    upsert_theory(
        chapter, 'js-quest-ce-que-javascript', "Qu'est-ce que JavaScript ?", 1,
        """# Qu'est-ce que JavaScript ?

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Expliquer le rôle de JavaScript dans une page web
- ✅ Inclure du JavaScript dans une page HTML
- ✅ Afficher un message dans la console avec `console.log`

---

## ⚡ Le troisième pilier du web

Vous connaissez déjà HTML (structure) et CSS (présentation). JavaScript est le **comportement** :
il permet à une page de **réagir** — afficher un message quand on clique sur un bouton, valider un
formulaire avant envoi, faire apparaître un menu, mettre à jour un contenu sans recharger la page...

> 💡 **Rappel de l'analogie de la maison** : HTML = les murs et fondations, CSS = la décoration,
> JavaScript = l'électricité et la domotique — ce qui rend la maison "vivante" et réactive.

Sans JavaScript, une page web est **statique** : elle affiche toujours la même chose, quoi que fasse
le visiteur.

---

## 📝 Où écrit-on du JavaScript ?

### 1️⃣ Dans un fichier séparé (recommandé)

```html
<script src="script.js"></script>
```

✅ Même logique que le CSS externe : réutilisable, mis en cache, sépare structure et comportement.

### 2️⃣ Directement dans la page

```html
<script>
    console.log("Bonjour !");
</script>
```

Pratique pour tester rapidement, mais moins maintenable sur un vrai projet.

> 💡 **Où placer `<script>` ?** Juste avant `</body>`, ou avec l'attribut `defer` dans le `<head>` :
> ça garantit que le HTML est déjà chargé avant que le JavaScript n'essaie de le manipuler.

---

## 🖥️ La console : votre meilleure amie pour débuter

```js
console.log("Bonjour depuis JavaScript !");
console.log(42);
console.log("La réponse est :", 42);
```

`console.log()` affiche un message dans la **console du navigateur** (accessible via les outils de
développement, touche F12). C'est l'outil n°1 pour comprendre ce que fait votre code : afficher la
valeur d'une variable, vérifier qu'une fonction est bien appelée, traquer un bug...

> 🎓 **Réflexe à prendre dès maintenant** : dès que vous ne comprenez pas pourquoi votre code ne fait
> pas ce que vous attendez, ajoutez des `console.log()` à différents endroits pour "espionner" ce qui
> se passe réellement.

---

## 🌍 JavaScript ne tourne pas que dans le navigateur

Ce chapitre se concentre sur JavaScript **côté navigateur** (manipuler une page web). Mais le même
langage tourne aussi côté serveur grâce à **Node.js** — d'ailleurs, c'est exactement ce qui exécute
vos exercices de code sur cette plateforme !

---

## 🎓 Points clés à retenir

✅ JavaScript ajoute le **comportement** et l'interactivité à une page HTML/CSS
✅ `<script src="...">` (externe, recommandé) ou `<script>...</script>` (interne)
✅ `console.log()` affiche des messages dans la console — votre outil de débogage principal
✅ JavaScript tourne dans le navigateur, mais aussi côté serveur avec Node.js

---

## 🚀 À vous de jouer !

Les prochaines leçons vous font manipuler du JavaScript directement dans l'éditeur de code de la
plateforme — pas besoin de fichier HTML pour l'instant, on se concentre sur le langage lui-même.
""",
        10, 10,
    )

    # ==========================================================================
    # 2. VARIABLES ET TYPES DE DONNÉES
    # ==========================================================================

    upsert_theory(
        chapter, 'js-variables-et-types', 'Variables et types de données', 2,
        """# Variables et types de données

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Déclarer une variable avec `let` et `const`
- ✅ Reconnaître les types de base : nombre, chaîne, booléen
- ✅ Utiliser `typeof` pour vérifier le type d'une valeur

---

## 📦 Une variable, c'est quoi ?

Une variable est une **boîte étiquetée** qui stocke une valeur pour pouvoir la réutiliser plus tard.

```js
let prenom = "Alex";
console.log(prenom); // Alex
```

---

## 🔒 `const` vs `let`

```js
const PI = 3.14159;   // ne pourra plus jamais changer
let score = 0;         // pourra changer plus tard
score = 10;             // ✅ autorisé
PI = 3;                 // ❌ Erreur ! const ne peut pas être réassigné
```

| Mot-clé | Peut être réassigné ? | Quand l'utiliser |
|---------|------------------------|--------------------|
| `const` | ❌ Non | Par défaut, dès que la valeur ne doit pas changer |
| `let` | ✅ Oui | Quand vous savez que la valeur va changer (compteur, score...) |

> 🎓 **Bonne pratique largement adoptée** : utiliser `const` par défaut, et ne passer à `let` que
> lorsque vous savez déjà que la variable devra être réassignée. Cela évite des bugs où une valeur
> change accidentellement sans que ce soit voulu.

> 🚫 Vous verrez parfois `var` dans du code ancien : c'est l'ancienne façon de déclarer une variable,
> avec un comportement plus difficile à prévoir. On ne l'utilise plus dans du code moderne.

---

## 🔤 Les types de données de base

```js
const age = 25;                    // number
const prenom = "Alex";             // string
const estMajeur = true;            // boolean
let futureValeur;                  // undefined (déclarée mais pas encore définie)
const rien = null;                 // null (absence de valeur, volontaire)
```

| Type | Exemple | Description |
|------|---------|--------------|
| `number` | `25`, `3.14`, `-8` | Tout nombre, entier ou décimal (pas de type séparé pour les décimaux) |
| `string` | `"Alex"`, `'Bonjour'` | Du texte, entre guillemets simples ou doubles |
| `boolean` | `true`, `false` | Une valeur vrai/faux |
| `undefined` | — | Une variable déclarée mais sans valeur assignée |
| `null` | — | Une absence de valeur **volontaire**, définie explicitement |

---

## 🔍 Vérifier un type avec `typeof`

```js
console.log(typeof 25);        // "number"
console.log(typeof "Alex");    // "string"
console.log(typeof true);      // "boolean"
```

---

## 🧵 Concaténer et interpoler du texte

```js
const prenom = "Alex";
const age = 25;

// Concaténation classique
console.log("Je m'appelle " + prenom + " et j'ai " + age + " ans.");

// Template literals (recommandé) : avec des backticks `...` et ${}
console.log(`Je m'appelle ${prenom} et j'ai ${age} ans.`);
```

> 💡 Les **template literals** (guillemets obliques `` ` ``) sont beaucoup plus lisibles dès qu'on
> mélange texte et variables — c'est la méthode recommandée en JavaScript moderne.

---

## 🎓 Points clés à retenir

✅ `const` par défaut, `let` seulement si la valeur doit changer
✅ 3 types de base : `number`, `string`, `boolean` (+ `undefined`/`null` pour l'absence de valeur)
✅ `typeof valeur` renvoie le type sous forme de texte
✅ Les template literals `` `${variable}` `` sont préférables à la concaténation avec `+`

---

## 🚀 À vous de jouer !
""",
        12, 10,
    )

    upsert_exercise(
        chapter, 'exercice-js-variables', 'Exercice rapide : les variables', 3,
        """# 🎯 Exercice rapide : les variables

## Objectif

Déclarer des variables des 3 types de base et une chaîne construite avec un template literal.

---

## 📋 Instructions

- [ ] Déclarez `const prenom` avec votre prénom (une chaîne)
- [ ] Déclarez `const age` avec un nombre
- [ ] Déclarez `const estEtudiant` avec `true` ou `false`
- [ ] Déclarez `const presentation` en utilisant un template literal incluant `prenom` et `age`

---

## ✅ Critères de validation

1. ✅ `prenom` est bien une chaîne de caractères
2. ✅ `age` est bien un nombre
3. ✅ `estEtudiant` est bien un booléen
4. ✅ `presentation` contient à la fois la valeur de `prenom` et celle de `age`

---

## 🚀 C'est parti !
""",
        """// Déclarez vos variables ici
const prenom = "";
const age = 0;
const estEtudiant = true;
const presentation = "";
""",
        """const prenom = "Alex";
const age = 25;
const estEtudiant = true;
const presentation = `Je m'appelle ${prenom} et j'ai ${age} ans.`;
""",
        [
            {"name": "prenom est une chaîne", "code": "assert.strictEqual(typeof prenom, 'string');", "points": 2, "error_message": "prenom doit être une chaîne de caractères"},
            {"name": "age est un nombre", "code": "assert.strictEqual(typeof age, 'number');", "points": 2, "error_message": "age doit être un nombre"},
            {"name": "estEtudiant est un booléen", "code": "assert.strictEqual(typeof estEtudiant, 'boolean');", "points": 2, "error_message": "estEtudiant doit être true ou false"},
            {"name": "presentation contient prenom et age", "code": "assert(presentation.includes(prenom) && presentation.includes(String(age)));", "points": 4, "error_message": "presentation doit contenir à la fois prenom et age"},
        ],
        [
            "💡 Astuce 1 : une chaîne s'écrit entre guillemets, un nombre sans guillemets",
            "💡 Astuce 2 : un template literal utilise des backticks : `Texte ${variable}`",
        ],
    )

    # ==========================================================================
    # 3. LES CONDITIONS
    # ==========================================================================

    upsert_theory(
        chapter, 'js-les-conditions', 'Les conditions', 4,
        """# Les conditions

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Écrire une condition avec `if` / `else if` / `else`
- ✅ Utiliser les opérateurs de comparaison, dont `===`
- ✅ Combiner des conditions avec `&&`, `||` et `!`

---

## 🔀 `if` / `else`

```js
const age = 20;

if (age >= 18) {
    console.log("Majeur");
} else {
    console.log("Mineur");
}
```

Le code entre `{ }` après `if (...)` ne s'exécute que si la condition est **vraie** (`true`).

## 🔀 Plusieurs cas avec `else if`

```js
const note = 14;

if (note >= 16) {
    console.log("Très bien");
} else if (note >= 12) {
    console.log("Bien");
} else if (note >= 10) {
    console.log("Passable");
} else {
    console.log("Insuffisant");
}
```

Les conditions sont testées **dans l'ordre**, et dès qu'une est vraie, les suivantes sont ignorées.

---

## ⚖️ Les opérateurs de comparaison

| Opérateur | Signification | Exemple |
|-----------|-----------------|---------|
| `===` | Égal (strict) | `5 === 5` → `true` |
| `!==` | Différent (strict) | `5 !== 3` → `true` |
| `>` / `<` | Supérieur / inférieur | `5 > 3` → `true` |
| `>=` / `<=` | Supérieur ou égal / inférieur ou égal | `5 >= 5` → `true` |

> ⚠️ **Toujours utiliser `===` et `!==`** (comparaison stricte), jamais `==`/`!=`. Ces derniers
> essaient de **convertir** les types avant de comparer (`"5" == 5` donne `true`, ce qui cause des
> bugs difficiles à comprendre). `===` compare la valeur **et** le type, sans conversion surprise.

```js
console.log("5" == 5);   // true  ⚠️ piégeux : convertit "5" en nombre avant de comparer
console.log("5" === 5);  // false ✅ prévisible : types différents (string vs number)
```

---

## 🔗 Combiner des conditions

```js
const age = 25;
const aPermis = true;

if (age >= 18 && aPermis) {
    console.log("Peut conduire");
}
```

| Opérateur | Signification | Exemple |
|-----------|-----------------|---------|
| `&&` | ET — les deux doivent être vraies | `age >= 18 && aPermis` |
| `\\|\\|` | OU — au moins une doit être vraie | `estAdmin \\|\\| estModerateur` |
| `!` | NON — inverse une valeur | `!estConnecte` |

```js
const estWeekend = true;
const estFerie = false;

if (estWeekend || estFerie) {
    console.log("Pas de travail aujourd'hui !");
}
```

---

## 🎓 Points clés à retenir

✅ `if (condition) { ... } else { ... }`, avec `else if` pour plusieurs cas
✅ Toujours utiliser `===`/`!==`, jamais `==`/`!=`
✅ `&&` (ET), `||` (OU), `!` (NON) pour combiner des conditions

---

## 🚀 À vous de jouer !
""",
        13, 10,
    )

    upsert_exercise(
        chapter, 'exercice-js-conditions', 'Exercice rapide : les conditions', 5,
        """# 🎯 Exercice rapide : les conditions

## Objectif

Écrire une fonction qui classe un nombre selon des tranches, avec if/else if/else.

---

## 📋 Instructions

Complétez la fonction `categoriser(note)` qui retourne :

- [ ] `"Très bien"` si `note >= 16`
- [ ] `"Bien"` si `note >= 12` (et < 16)
- [ ] `"Passable"` si `note >= 10` (et < 12)
- [ ] `"Insuffisant"` sinon

---

## ✅ Critères de validation

1. ✅ `categoriser(18)` retourne `"Très bien"`
2. ✅ `categoriser(13)` retourne `"Bien"`
3. ✅ `categoriser(10)` retourne `"Passable"`
4. ✅ `categoriser(5)` retourne `"Insuffisant"`

---

## 🚀 C'est parti !
""",
        """function categoriser(note) {
    // Complétez avec if / else if / else
}
""",
        """function categoriser(note) {
    if (note >= 16) {
        return "Très bien";
    } else if (note >= 12) {
        return "Bien";
    } else if (note >= 10) {
        return "Passable";
    } else {
        return "Insuffisant";
    }
}
""",
        [
            {"name": "categoriser(18) -> Très bien", "code": "assert.strictEqual(categoriser(18), 'Très bien');", "points": 3, "error_message": "categoriser(18) doit retourner \"Très bien\""},
            {"name": "categoriser(13) -> Bien", "code": "assert.strictEqual(categoriser(13), 'Bien');", "points": 3, "error_message": "categoriser(13) doit retourner \"Bien\""},
            {"name": "categoriser(10) -> Passable", "code": "assert.strictEqual(categoriser(10), 'Passable');", "points": 2, "error_message": "categoriser(10) doit retourner \"Passable\""},
            {"name": "categoriser(5) -> Insuffisant", "code": "assert.strictEqual(categoriser(5), 'Insuffisant');", "points": 2, "error_message": "categoriser(5) doit retourner \"Insuffisant\""},
        ],
        [
            "💡 Astuce 1 : testez les conditions du plus grand seuil au plus petit",
            "💡 Astuce 2 : n'oubliez pas le mot-clé return dans chaque branche",
        ],
    )

    # ==========================================================================
    # 4. LES BOUCLES
    # ==========================================================================

    upsert_theory(
        chapter, 'js-les-boucles', 'Les boucles', 6,
        """# Les boucles

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Répéter du code un nombre défini de fois avec `for`
- ✅ Répéter du code tant qu'une condition est vraie avec `while`
- ✅ Éviter le piège de la boucle infinie

---

## 🔁 La boucle `for`

```js
for (let i = 0; i < 5; i++) {
    console.log(i);
}
// Affiche : 0 1 2 3 4
```

La boucle `for` a 3 parties, séparées par `;` :

| Partie | Rôle | Ici |
|--------|------|-----|
| Initialisation | Exécutée une seule fois, au départ | `let i = 0` |
| Condition | Vérifiée avant chaque tour, la boucle continue tant qu'elle est vraie | `i < 5` |
| Incrémentation | Exécutée après chaque tour | `i++` (équivaut à `i = i + 1`) |

> 💡 **Cas d'usage classique** : parcourir un tableau, répéter une action un nombre précis de fois.

### Exemple : additionner des nombres

```js
let somme = 0;
for (let i = 1; i <= 10; i++) {
    somme = somme + i; // ou : somme += i;
}
console.log(somme); // 55
```

---

## 🔁 La boucle `while`

```js
let compteur = 0;
while (compteur < 3) {
    console.log(compteur);
    compteur++;
}
// Affiche : 0 1 2
```

`while` répète le bloc **tant que** la condition reste vraie. Utile quand on ne sait pas à l'avance
combien de tours seront nécessaires (ex : "tant que l'utilisateur n'a pas entré un mot de passe
correct").

> 🚫 **Piège classique : la boucle infinie**. Si la condition ne devient jamais fausse (ex : on oublie
> `compteur++`), la boucle tourne indéfiniment et bloque le programme. **Toujours vérifier qu'il existe
> un moyen pour la condition de devenir fausse.**

```js
// ❌ Boucle infinie : compteur n'est jamais modifié !
let compteur = 0;
while (compteur < 3) {
    console.log(compteur);
    // oubli de compteur++
}
```

---

## ⏭️ `break` et `continue`

```js
for (let i = 0; i < 10; i++) {
    if (i === 5) {
        break; // arrête complètement la boucle
    }
    console.log(i);
}
// Affiche : 0 1 2 3 4

for (let i = 0; i < 5; i++) {
    if (i === 2) {
        continue; // passe directement au tour suivant, sans exécuter la suite
    }
    console.log(i);
}
// Affiche : 0 1 3 4 (le 2 est sauté)
```

---

## 🎓 Points clés à retenir

✅ `for` : nombre de répétitions connu à l'avance
✅ `while` : répète tant qu'une condition reste vraie
✅ Toujours s'assurer que la condition peut devenir fausse (éviter les boucles infinies)
✅ `break` arrête la boucle, `continue` passe au tour suivant

---

## 🚀 À vous de jouer !
""",
        13, 10,
    )

    upsert_exercise(
        chapter, 'exercice-js-boucles', 'Exercice rapide : les boucles', 7,
        """# 🎯 Exercice rapide : les boucles

## Objectif

Calculer la somme des nombres de 1 à N avec une boucle for.

---

## 📋 Instructions

Complétez la fonction `sommeJusqua(n)` qui retourne la somme de tous les nombres entiers de `1` à `n`
inclus, en utilisant une boucle `for`.

---

## ✅ Critères de validation

1. ✅ `sommeJusqua(5)` retourne `15` (1+2+3+4+5)
2. ✅ `sommeJusqua(10)` retourne `55`
3. ✅ `sommeJusqua(1)` retourne `1`

---

## 🚀 C'est parti !
""",
        """function sommeJusqua(n) {
    let somme = 0;
    // Complétez avec une boucle for
    return somme;
}
""",
        """function sommeJusqua(n) {
    let somme = 0;
    for (let i = 1; i <= n; i++) {
        somme += i;
    }
    return somme;
}
""",
        [
            {"name": "sommeJusqua(5) -> 15", "code": "assert.strictEqual(sommeJusqua(5), 15);", "points": 4, "error_message": "sommeJusqua(5) doit retourner 15"},
            {"name": "sommeJusqua(10) -> 55", "code": "assert.strictEqual(sommeJusqua(10), 55);", "points": 4, "error_message": "sommeJusqua(10) doit retourner 55"},
            {"name": "sommeJusqua(1) -> 1", "code": "assert.strictEqual(sommeJusqua(1), 1);", "points": 2, "error_message": "sommeJusqua(1) doit retourner 1"},
        ],
        [
            "💡 Astuce 1 : for (let i = 1; i <= n; i++) { ... }",
            "💡 Astuce 2 : n'oubliez pas de retourner somme à la fin",
        ],
    )

    # ==========================================================================
    # 5. LES FONCTIONS
    # ==========================================================================

    upsert_theory(
        chapter, 'js-les-fonctions', 'Les fonctions', 8,
        """# Les fonctions

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Déclarer une fonction avec des paramètres et un `return`
- ✅ Appeler une fonction et récupérer sa valeur de retour
- ✅ Reconnaître la syntaxe des fonctions fléchées (*arrow functions*)

---

## 🧰 Une fonction, c'est quoi ?

Une fonction est un **bloc de code réutilisable**, auquel on donne un nom, qu'on peut appeler autant
de fois qu'on veut, avec des données différentes à chaque fois.

```js
function direBonjour(prenom) {
    return `Bonjour, ${prenom} !`;
}

console.log(direBonjour("Alex"));  // Bonjour, Alex !
console.log(direBonjour("Sam"));   // Bonjour, Sam !
```

- `direBonjour` : le nom de la fonction
- `prenom` : un **paramètre** — une valeur d'entrée que la fonction attend
- `return` : la **valeur de sortie**, renvoyée à celui qui a appelé la fonction

> 💡 **Analogie** : une fonction est comme une recette de cuisine. Les paramètres sont les
> ingrédients, le code à l'intérieur est la préparation, et `return` est le plat obtenu à la fin.

---

## ⚠️ `return` arrête immédiatement la fonction

```js
function estMajeur(age) {
    if (age >= 18) {
        return true;
    }
    return false;
}
```

Dès qu'un `return` est exécuté, la fonction s'arrête **immédiatement** — le code après n'est jamais
exécuté pour cet appel.

## 🔢 Plusieurs paramètres

```js
function addition(a, b) {
    return a + b;
}

console.log(addition(2, 3)); // 5
```

---

## 🏹 Les fonctions fléchées (*arrow functions*)

Une syntaxe plus courte et très répandue en JavaScript moderne :

```js
// Fonction classique
function addition(a, b) {
    return a + b;
}

// Fonction fléchée équivalente
const addition = (a, b) => {
    return a + b;
};

// Encore plus court : si le corps ne fait qu'un "return", on peut l'omettre
const addition = (a, b) => a + b;
```

Les 3 écritures ci-dessus font exactement la même chose. Vous croiserez très souvent la syntaxe
fléchée dans du code JavaScript moderne (et notamment avec les tableaux, dans la prochaine leçon).

---

## 🎁 Une fonction sans `return` renvoie `undefined`

```js
function direBonjour(prenom) {
    console.log(`Bonjour, ${prenom}`); // affiche, mais ne "retourne" rien
}

const resultat = direBonjour("Alex"); // affiche "Bonjour, Alex"
console.log(resultat); // undefined — la fonction n'a rien "return"é
```

> 🚫 **Confusion fréquente chez les débutants** : `console.log()` **affiche** une valeur (pour vous,
> dans la console), alors que `return` **renvoie** une valeur (pour que le reste du programme
> puisse l'utiliser). Les deux sont utiles, mais ne font pas la même chose.

---

## 🎓 Points clés à retenir

✅ `function nom(paramètres) { ... return valeur; }`
✅ Une fonction s'arrête dès qu'elle rencontre un `return`
✅ Les fonctions fléchées `(a, b) => a + b` sont une syntaxe plus courte, très utilisée
✅ `console.log` affiche, `return` renvoie une valeur utilisable — ce n'est pas la même chose

---

## 🚀 À vous de jouer !
""",
        13, 10,
    )

    upsert_exercise(
        chapter, 'exercice-js-fonctions', 'Exercice rapide : les fonctions', 9,
        """# 🎯 Exercice rapide : les fonctions

## Objectif

Écrire une fonction avec deux paramètres qui retourne une valeur calculée.

---

## 📋 Instructions

Complétez la fonction `calculerPrixTotal(prixUnitaire, quantite)` qui retourne le prix total
(`prixUnitaire * quantite`).

---

## ✅ Critères de validation

1. ✅ `calculerPrixTotal(10, 3)` retourne `30`
2. ✅ `calculerPrixTotal(5, 0)` retourne `0`
3. ✅ `calculerPrixTotal(2.5, 4)` retourne `10`

---

## 🚀 C'est parti !
""",
        """function calculerPrixTotal(prixUnitaire, quantite) {
    // Complétez avec un return
}
""",
        """function calculerPrixTotal(prixUnitaire, quantite) {
    return prixUnitaire * quantite;
}
""",
        [
            {"name": "calculerPrixTotal(10, 3) -> 30", "code": "assert.strictEqual(calculerPrixTotal(10, 3), 30);", "points": 4, "error_message": "calculerPrixTotal(10, 3) doit retourner 30"},
            {"name": "calculerPrixTotal(5, 0) -> 0", "code": "assert.strictEqual(calculerPrixTotal(5, 0), 0);", "points": 3, "error_message": "calculerPrixTotal(5, 0) doit retourner 0"},
            {"name": "calculerPrixTotal(2.5, 4) -> 10", "code": "assert.strictEqual(calculerPrixTotal(2.5, 4), 10);", "points": 3, "error_message": "calculerPrixTotal(2.5, 4) doit retourner 10"},
        ],
        [
            "💡 Astuce 1 : return prixUnitaire * quantite;",
            "💡 Astuce 2 : n'oubliez pas le mot-clé return, sinon la fonction renvoie undefined",
        ],
    )

    # ==========================================================================
    # 6. LES TABLEAUX
    # ==========================================================================

    upsert_theory(
        chapter, 'js-les-tableaux', 'Les tableaux', 10,
        """# Les tableaux

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Créer un tableau et accéder à ses éléments par index
- ✅ Ajouter des éléments avec `push`
- ✅ Parcourir un tableau avec `for` et avec `forEach`

---

## 📚 Un tableau, c'est quoi ?

Un tableau stocke une **liste ordonnée** de valeurs, dans une seule variable.

```js
const fruits = ["Pomme", "Banane", "Orange"];
console.log(fruits); // [ 'Pomme', 'Banane', 'Orange' ]
```

---

## 🔢 Accéder à un élément par index

```js
const fruits = ["Pomme", "Banane", "Orange"];

console.log(fruits[0]); // Pomme
console.log(fruits[1]); // Banane
console.log(fruits[2]); // Orange
```

> ⚠️ **Les index commencent à 0**, pas à 1 ! Le premier élément est `fruits[0]`, pas `fruits[1]`.
> C'est l'une des sources de confusion les plus fréquentes chez les débutants.

## 📏 La longueur du tableau

```js
console.log(fruits.length); // 3
console.log(fruits[fruits.length - 1]); // Orange (dernier élément)
```

---

## ➕ Ajouter un élément : `push`

```js
const fruits = ["Pomme", "Banane"];
fruits.push("Orange");
console.log(fruits); // [ 'Pomme', 'Banane', 'Orange' ]
console.log(fruits.length); // 3
```

`push()` ajoute un élément **à la fin** du tableau, et modifie le tableau existant.

---

## 🔁 Parcourir un tableau avec `for`

```js
const fruits = ["Pomme", "Banane", "Orange"];

for (let i = 0; i < fruits.length; i++) {
    console.log(fruits[i]);
}
```

## 🔁 Parcourir un tableau avec `forEach` (plus moderne)

```js
fruits.forEach((fruit) => {
    console.log(fruit);
});
```

`forEach` appelle la fonction fléchée une fois pour **chaque élément** du tableau — plus lisible que
la boucle `for` classique quand on n'a pas besoin de l'index.

---

## 🆚 `for` vs `forEach`

| | `for` | `forEach` |
|---|-------|-----------|
| Accès à l'index | Facile (`i`) | Possible mais moins direct |
| Lisibilité | Plus verbeux | Plus concis |
| `break`/`continue` | ✅ Possible | ❌ Impossible |

---

## ✅ Exemple complet

```js
const notes = [12, 8, 15, 20, 6];
let somme = 0;

for (let i = 0; i < notes.length; i++) {
    somme += notes[i];
}

const moyenne = somme / notes.length;
console.log(`Moyenne : ${moyenne}`);
```

---

## 🎓 Points clés à retenir

✅ Un tableau `[a, b, c]` stocke une liste ordonnée, accessible par index (à partir de **0**)
✅ `tableau.length` donne le nombre d'éléments
✅ `tableau.push(valeur)` ajoute un élément à la fin
✅ `for` (accès index) ou `forEach` (plus lisible) pour parcourir un tableau

---

## 🚀 À vous de jouer !
""",
        13, 10,
    )

    upsert_exercise(
        chapter, 'exercice-js-tableaux', 'Exercice rapide : les tableaux', 11,
        """# 🎯 Exercice rapide : les tableaux

## Objectif

Calculer la somme des éléments d'un tableau de nombres.

---

## 📋 Instructions

Complétez la fonction `sommeTableau(nombres)` qui retourne la somme de tous les éléments du tableau
`nombres` passé en paramètre.

---

## ✅ Critères de validation

1. ✅ `sommeTableau([1, 2, 3])` retourne `6`
2. ✅ `sommeTableau([10, 20, 30, 40])` retourne `100`
3. ✅ `sommeTableau([])` retourne `0`

---

## 🚀 C'est parti !
""",
        """function sommeTableau(nombres) {
    let somme = 0;
    // Parcourez le tableau et additionnez chaque élément
    return somme;
}
""",
        """function sommeTableau(nombres) {
    let somme = 0;
    for (let i = 0; i < nombres.length; i++) {
        somme += nombres[i];
    }
    return somme;
}
""",
        [
            {"name": "sommeTableau([1,2,3]) -> 6", "code": "assert.strictEqual(sommeTableau([1, 2, 3]), 6);", "points": 4, "error_message": "sommeTableau([1, 2, 3]) doit retourner 6"},
            {"name": "sommeTableau([10,20,30,40]) -> 100", "code": "assert.strictEqual(sommeTableau([10, 20, 30, 40]), 100);", "points": 3, "error_message": "sommeTableau([10, 20, 30, 40]) doit retourner 100"},
            {"name": "sommeTableau([]) -> 0", "code": "assert.strictEqual(sommeTableau([]), 0);", "points": 3, "error_message": "sommeTableau([]) doit retourner 0 (tableau vide)"},
        ],
        [
            "💡 Astuce 1 : for (let i = 0; i < nombres.length; i++) { somme += nombres[i]; }",
            "💡 Astuce 2 : un tableau vide a une longueur (length) de 0, la boucle ne s'exécute alors jamais",
        ],
    )

    # ==========================================================================
    # 7. MANIPULER LE DOM
    # ==========================================================================

    upsert_theory(
        chapter, 'js-manipuler-le-dom', 'Manipuler le DOM', 12,
        """# Manipuler le DOM

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Sélectionner un élément HTML avec `document.querySelector`
- ✅ Modifier son contenu et son style
- ✅ Ajouter/retirer une classe CSS dynamiquement

---

## 🌳 Le DOM, qu'est-ce que c'est ?

Le **DOM** (*Document Object Model*) est la représentation de votre page HTML sous forme d'objets
que JavaScript peut lire et modifier. Concrètement : le DOM est le pont entre votre HTML statique et
JavaScript, qui peut désormais le manipuler **après** le chargement de la page.

> 💡 **Analogie** : le HTML que vous écrivez est la recette. Le DOM est le plat une fois préparé, que
> JavaScript peut encore modifier (ajouter du sel, changer la présentation) après la cuisson.

---

## 🔍 Sélectionner un élément : `querySelector`

```js
const titre = document.querySelector('h1');
const bouton = document.querySelector('.mon-bouton'); // sélecteur de classe
const zone = document.querySelector('#zone-message'); // sélecteur d'ID
```

`document.querySelector(selecteur)` accepte **exactement la même syntaxe** que les sélecteurs CSS que
vous connaissez déjà (`h1`, `.classe`, `#id`) — et renvoie le **premier** élément qui correspond.

---

## ✏️ Modifier le contenu

```js
const titre = document.querySelector('h1');
titre.textContent = "Nouveau titre !";
```

`textContent` lit ou modifie le texte contenu dans un élément.

## 🎨 Modifier le style directement

```js
const carte = document.querySelector('.carte');
carte.style.backgroundColor = "yellow";
carte.style.fontSize = "20px";
```

> 💡 Les propriétés CSS en JavaScript s'écrivent en *camelCase* (`backgroundColor`) plutôt qu'avec des
> tirets (`background-color`), car le tiret a un sens spécial en JavaScript (une soustraction !).

## 🏷️ Ajouter/retirer une classe CSS : `classList`

```js
const carte = document.querySelector('.carte');

carte.classList.add('actif');       // ajoute la classe "actif"
carte.classList.remove('actif');    // retire la classe "actif"
carte.classList.toggle('actif');    // ajoute si absente, retire si présente
```

> 🎓 **Bonne pratique** : plutôt que de modifier `style` propriété par propriété en JavaScript, il est
> souvent préférable de définir l'apparence voulue dans une classe CSS, puis d'ajouter/retirer cette
> classe avec `classList` — ça garde la présentation (CSS) séparée du comportement (JavaScript).

---

## ✅ Exemple complet

```js
const bouton = document.querySelector('.bouton-like');
const compteur = document.querySelector('.compteur');

let nombreLikes = 0;

// (le clic sera vu dans la prochaine leçon, sur les événements)
nombreLikes = nombreLikes + 1;
compteur.textContent = nombreLikes;
bouton.classList.add('like-actif');
```

---

## 🎓 Points clés à retenir

✅ Le DOM est la représentation de la page que JavaScript peut manipuler
✅ `document.querySelector(sélecteur)` utilise la même syntaxe que les sélecteurs CSS
✅ `textContent` pour le texte, `.style.propriete` pour un style ponctuel
✅ `classList.add/remove/toggle` pour ajouter/retirer une classe CSS (à préférer à `style` répété)

---

## 🚀 À vous de jouer !
""",
        13, 10,
    )

    upsert_exercise(
        chapter, 'exercice-js-dom', 'Exercice rapide : manipuler le DOM', 13,
        """# 🎯 Exercice rapide : manipuler le DOM

## Objectif

Sélectionner un élément, modifier son texte et lui ajouter une classe.

---

## 📋 Instructions

- [ ] Sélectionnez l'élément `.message` avec `document.querySelector`
- [ ] Modifiez son `textContent`
- [ ] Ajoutez-lui la classe `"visible"` avec `classList.add`

---

## ✅ Critères de validation

1. ✅ Le code utilise `document.querySelector`
2. ✅ Le code modifie `textContent`
3. ✅ Le code utilise `classList.add`

---

## 🚀 C'est parti !
""",
        """// Sélectionnez .message, changez son texte, ajoutez-lui la classe "visible"
""",
        """const message = document.querySelector('.message');
message.textContent = "Bienvenue !";
message.classList.add('visible');
""",
        [
            {"name": "utilise querySelector", "code": "assert(__source.includes('querySelector'));", "points": 3, "error_message": "Utilisez document.querySelector(...) pour sélectionner l'élément"},
            {"name": "modifie textContent", "code": "assert(__source.includes('textContent'));", "points": 3, "error_message": "Modifiez le textContent de l'élément sélectionné"},
            {"name": "utilise classList.add", "code": "assert(__source.includes('classList.add'));", "points": 4, "error_message": "Ajoutez la classe avec classList.add('visible')"},
        ],
        [
            "💡 Astuce 1 : const message = document.querySelector('.message');",
            "💡 Astuce 2 : message.classList.add('visible');",
        ],
    )

    # ==========================================================================
    # 8. LES ÉVÉNEMENTS
    # ==========================================================================

    upsert_theory(
        chapter, 'js-les-evenements', 'Les événements', 14,
        """# Les événements

## 🎯 Objectifs de cette leçon

À la fin de cette leçon, vous serez capable de :
- ✅ Réagir à un clic avec `addEventListener`
- ✅ Comprendre le rôle de la fonction "callback"
- ✅ Reconnaître quelques événements courants

---

## 🖱️ Écouter un événement : `addEventListener`

```js
const bouton = document.querySelector('.mon-bouton');

bouton.addEventListener('click', function () {
    console.log("Le bouton a été cliqué !");
});
```

`addEventListener(evenement, fonction)` prend deux arguments :
- Le **nom de l'événement** à écouter (`'click'`, `'submit'`...)
- Une **fonction** à exécuter quand cet événement se produit (appelée *callback*, "fonction de rappel")

> 💡 La fonction callback n'est **pas appelée tout de suite** : elle est "mise de côté" et exécutée
> **plus tard**, uniquement quand l'événement se produit réellement (le clic).

Avec une fonction fléchée (syntaxe plus moderne, équivalente) :

```js
bouton.addEventListener('click', () => {
    console.log("Cliqué !");
});
```

---

## 📋 Quelques événements courants

| Événement | Se déclenche quand... |
|-----------|--------------------------|
| `click` | L'utilisateur clique sur l'élément |
| `submit` | Un formulaire est soumis |
| `input` | La valeur d'un champ change (à chaque frappe) |
| `mouseover` | La souris survole l'élément |
| `keydown` | Une touche du clavier est enfoncée |

---

## 🎯 L'objet événement

La fonction callback reçoit automatiquement un **objet événement**, souvent nommé `event` ou `e`,
qui contient des informations sur ce qui s'est passé.

```js
const formulaire = document.querySelector('form');

formulaire.addEventListener('submit', (event) => {
    event.preventDefault(); // empêche le rechargement de page par défaut
    console.log("Formulaire soumis sans recharger la page !");
});
```

`event.preventDefault()` est **essentiel** sur un formulaire : sans lui, le navigateur recharge la
page dès la soumission (comportement HTML par défaut), ce qui interromprait votre JavaScript.

---

## ✅ Exemple complet : un compteur de clics

```js
const bouton = document.querySelector('.bouton-like');
const compteur = document.querySelector('.compteur');
let nombreLikes = 0;

bouton.addEventListener('click', () => {
    nombreLikes = nombreLikes + 1;
    compteur.textContent = nombreLikes;
});
```

À chaque clic sur `.bouton-like`, la fonction callback s'exécute : elle incrémente `nombreLikes` et
met à jour l'affichage.

---

## 🎓 Points clés à retenir

✅ `element.addEventListener('evenement', callback)` réagit à une interaction
✅ La fonction callback n'est exécutée que lorsque l'événement se produit réellement
✅ `event.preventDefault()` empêche le comportement par défaut du navigateur (utile sur `submit`)
✅ `click`, `submit`, `input` sont les événements les plus courants pour débuter

---

## 🚀 À vous de jouer !
""",
        13, 10,
    )

    upsert_exercise(
        chapter, 'exercice-js-evenements', 'Exercice rapide : les événements', 15,
        """# 🎯 Exercice rapide : les événements

## Objectif

Écouter un clic sur un bouton et mettre à jour un élément en réponse.

---

## 📋 Instructions

- [ ] Sélectionnez `.bouton` et `.compteur`
- [ ] Ajoutez un écouteur `'click'` sur `.bouton` avec `addEventListener`
- [ ] Dans le callback, mettez à jour `textContent` de `.compteur`

---

## ✅ Critères de validation

1. ✅ Le code utilise `addEventListener`
2. ✅ Le code écoute l'événement `'click'`
3. ✅ Le code modifie `textContent` à l'intérieur du callback

---

## 🚀 C'est parti !
""",
        """// Sélectionnez .bouton et .compteur, puis écoutez le clic
""",
        """const bouton = document.querySelector('.bouton');
const compteur = document.querySelector('.compteur');
let total = 0;

bouton.addEventListener('click', () => {
    total = total + 1;
    compteur.textContent = total;
});
""",
        [
            {"name": "utilise addEventListener", "code": "assert(__source.includes('addEventListener'));", "points": 3, "error_message": "Utilisez element.addEventListener('click', ...)"},
            {"name": "écoute l'événement click", "code": "assert(__source.includes(\"'click'\") || __source.includes('\"click\"'));", "points": 3, "error_message": "L'événement écouté doit être 'click'"},
            {"name": "modifie textContent dans le callback", "code": "assert(__source.includes('textContent'));", "points": 4, "error_message": "Mettez à jour textContent à l'intérieur du callback"},
        ],
        [
            "💡 Astuce 1 : bouton.addEventListener('click', () => { ... });",
            "💡 Astuce 2 : compteur.textContent = total; à l'intérieur du callback",
        ],
    )

    # ==========================================================================
    # GROS EXERCICES INTÉGRATEURS
    # ==========================================================================

    upsert_exercise(
        chapter, 'exercice-js-fizzbuzz', 'Exercice : FizzBuzz', 16,
        """# 🎯 Exercice : FizzBuzz

## Objectif

Un grand classique pour combiner boucles, conditions et tableaux !

---

## 📋 Instructions

Complétez la fonction `fizzBuzz(n)` qui retourne un **tableau** contenant, pour chaque nombre de `1`
à `n` inclus :

- [ ] `"Fizz"` si le nombre est un multiple de 3
- [ ] `"Buzz"` si le nombre est un multiple de 5
- [ ] `"FizzBuzz"` si le nombre est un multiple de 3 **et** de 5
- [ ] Le nombre lui-même (converti en texte) sinon

**Exemple** : `fizzBuzz(5)` doit retourner `["1", "2", "Fizz", "4", "Buzz"]`

---

## 💡 Conseils

- L'opérateur `%` (modulo) donne le reste d'une division : `6 % 3` vaut `0` (6 est un multiple de 3)
- Testez d'abord le cas "multiple de 3 ET de 5", avant les cas séparés

---

## ✅ Critères de validation

1. ✅ `fizzBuzz(5)` retourne `["1", "2", "Fizz", "4", "Buzz"]`
2. ✅ `fizzBuzz(15)[14]` vaut `"FizzBuzz"` (15 est multiple de 3 et 5)
3. ✅ `fizzBuzz(3)[2]` vaut `"Fizz"`
4. ✅ Le tableau retourné a la bonne longueur (`fizzBuzz(20).length === 20`)

---

## 🚀 C'est parti !
""",
        """function fizzBuzz(n) {
    const resultat = [];
    for (let i = 1; i <= n; i++) {
        // Complétez avec les conditions Fizz / Buzz / FizzBuzz / nombre
    }
    return resultat;
}
""",
        """function fizzBuzz(n) {
    const resultat = [];
    for (let i = 1; i <= n; i++) {
        if (i % 3 === 0 && i % 5 === 0) {
            resultat.push("FizzBuzz");
        } else if (i % 3 === 0) {
            resultat.push("Fizz");
        } else if (i % 5 === 0) {
            resultat.push("Buzz");
        } else {
            resultat.push(String(i));
        }
    }
    return resultat;
}
""",
        [
            {"name": "fizzBuzz(5) correct", "code": "assert.deepStrictEqual(fizzBuzz(5), ['1', '2', 'Fizz', '4', 'Buzz']);", "points": 8, "error_message": "fizzBuzz(5) doit retourner ['1', '2', 'Fizz', '4', 'Buzz']"},
            {"name": "multiple de 3 et 5 -> FizzBuzz", "code": "assert.strictEqual(fizzBuzz(15)[14], 'FizzBuzz');", "points": 6, "error_message": "Le 15e élément (index 14) doit être 'FizzBuzz'"},
            {"name": "multiple de 3 -> Fizz", "code": "assert.strictEqual(fizzBuzz(3)[2], 'Fizz');", "points": 5, "error_message": "Le 3e élément (index 2) doit être 'Fizz'"},
            {"name": "longueur correcte", "code": "assert.strictEqual(fizzBuzz(20).length, 20);", "points": 6, "error_message": "fizzBuzz(20) doit retourner un tableau de 20 éléments"},
        ],
        [
            "💡 Astuce 1 : testez d'abord (i % 3 === 0 && i % 5 === 0), sinon Fizz/Buzz s'affichera avant FizzBuzz",
            "💡 Astuce 2 : String(i) convertit le nombre i en texte",
        ],
        duration=20, points=25, difficulty='MEDIUM',
    )

    upsert_exercise(
        chapter, 'exercice-js-widget-dom', 'Exercice : un petit widget interactif', 17,
        """# 🎯 Exercice : un petit widget interactif

## Objectif

Combiner sélection DOM, texte, classe CSS et gestion d'un clic dans un seul petit script.

---

## 📋 Instructions

Écrivez un script qui :

- [ ] Sélectionne `.widget-titre` et modifie son `textContent`
- [ ] Sélectionne `.widget-bouton`
- [ ] Ajoute un écouteur `'click'` sur ce bouton
- [ ] Dans le callback, ajoute la classe `"ouvert"` à un élément `.widget-panneau` via `classList.add`

---

## ✅ Critères de validation

1. ✅ Utilise `querySelector` au moins 2 fois
2. ✅ Modifie `textContent`
3. ✅ Utilise `addEventListener` avec `'click'`
4. ✅ Utilise `classList.add` à l'intérieur du callback

---

## 🚀 C'est parti !
""",
        """// Construisez votre widget ici
""",
        """const titre = document.querySelector('.widget-titre');
titre.textContent = "Mon Widget";

const bouton = document.querySelector('.widget-bouton');
const panneau = document.querySelector('.widget-panneau');

bouton.addEventListener('click', () => {
    panneau.classList.add('ouvert');
});
""",
        [
            {"name": "au moins 2 querySelector", "code": "const __count = (__source.match(/querySelector/g) || []).length;\nassert(__count >= 2);", "points": 3, "error_message": "Utilisez querySelector au moins 2 fois"},
            {"name": "modifie textContent", "code": "assert(__source.includes('textContent'));", "points": 3, "error_message": "Modifiez le textContent du titre"},
            {"name": "addEventListener sur click", "code": "assert(__source.includes('addEventListener') && (__source.includes(\"'click'\") || __source.includes('\"click\"')));", "points": 3, "error_message": "Ajoutez un addEventListener('click', ...)"},
            {"name": "classList.add dans le callback", "code": "assert(__source.includes('classList.add'));", "points": 4, "error_message": "Ajoutez une classe avec classList.add(...) dans le callback"},
        ],
        [
            "💡 Astuce 1 : reprenez la structure de l'exercice précédent sur les événements",
            "💡 Astuce 2 : le classList.add doit être À L'INTÉRIEUR de la fonction callback du clic",
        ],
        duration=15, points=20, difficulty='MEDIUM',
    )
