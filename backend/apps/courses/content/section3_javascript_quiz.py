"""
Ajoute le quiz final du chapitre JavaScript (même format que les quiz
HTML/CSS déjà corrigés : options en liste plate, correct_answer par index,
positions volontairement variées).
"""

import copy
import random

from apps.courses.models import Chapter, Lesson, Quiz


def reorder_question(question, rng):
    """Mélange l'ordre des options d'une question ; le texte de la bonne
    réponse ne change pas, seule sa position change."""
    options = question['options']
    n = len(options)
    permutation = list(range(n))
    rng.shuffle(permutation)

    new_options = [options[i] for i in permutation]
    position_map = {old: new for new, old in enumerate(permutation)}

    old_correct = question['correct_answer']
    if isinstance(old_correct, list):
        new_correct = sorted(position_map[i] for i in old_correct)
    else:
        new_correct = position_map[old_correct]

    question['options'] = new_options
    question['correct_answer'] = new_correct
    return question


def verify_unchanged(original, reordered):
    for orig, fixed in zip(original, reordered):
        orig_correct = orig['correct_answer']
        orig_texts = (
            {orig['options'][i] for i in orig_correct}
            if isinstance(orig_correct, list)
            else {orig['options'][orig_correct]}
        )
        fixed_correct = fixed['correct_answer']
        fixed_texts = (
            {fixed['options'][i] for i in fixed_correct}
            if isinstance(fixed_correct, list)
            else {fixed['options'][fixed_correct]}
        )
        assert orig_texts == fixed_texts, f"MISMATCH on question {orig['id']}"
        assert set(orig['options']) == set(fixed['options']), f"Options changed on question {orig['id']}"


def build():
    """Construit ou met a jour ce bloc de contenu. Idempotent."""
    chapter = Chapter.objects.get(slug='introduction-javascript')

    quiz_lesson, _ = Lesson.objects.update_or_create(
        slug='quiz-js-fondamentaux',
        defaults={
            'chapter': chapter,
            'title': 'Quiz : Les Fondamentaux de JavaScript',
            'lesson_type': 'QUIZ',
            'order_index': 18,
            'content': '',
            'estimated_duration': 20,
            'points': 100,
            'is_published': True,
        }
    )

    quiz_questions = [
        {
            "id": 1, "type": "single",
            "question": "Quel mot-clé utiliser par défaut pour déclarer une variable qui ne sera jamais réassignée ?",
            "options": ["var", "let", "const", "static"],
            "correct_answer": 2,
            "explanation": "const est recommandé par défaut ; let seulement si la variable doit changer.",
        },
        {
            "id": 2, "type": "single",
            "question": "Que retourne typeof \"25\" ?",
            "options": ["\"number\"", "\"string\"", "\"boolean\"", "\"undefined\""],
            "correct_answer": 1,
            "explanation": "\"25\" est entre guillemets, donc une chaîne de caractères, pas un nombre.",
        },
        {
            "id": 3, "type": "single",
            "question": "Pourquoi préfère-t-on === à == en JavaScript ?",
            "options": [
                "=== est plus rapide à taper",
                "== n'existe plus dans les versions récentes",
                "=== compare aussi le type, sans conversion surprise",
                "Il n'y a aucune différence",
            ],
            "correct_answer": 2,
            "explanation": "== convertit les types avant de comparer (ex: \"5\" == 5 est vrai), ce qui cause des bugs difficiles à repérer.",
        },
        {
            "id": 4, "type": "single",
            "question": "Que fait l'opérateur && dans une condition ?",
            "options": [
                "Il inverse une valeur booléenne",
                "Il vérifie qu'au moins une des conditions est vraie",
                "Il vérifie que les deux conditions sont vraies",
                "Il additionne deux nombres",
            ],
            "correct_answer": 2,
            "explanation": "&& (ET) exige que les deux conditions soient vraies ; || (OU) exige qu'au moins une le soit.",
        },
        {
            "id": 5, "type": "single",
            "question": "Dans for (let i = 0; i < 5; i++) { ... }, combien de fois le bloc s'exécute-t-il ?",
            "options": ["4 fois", "6 fois", "5 fois", "Une infinité de fois"],
            "correct_answer": 2,
            "explanation": "i vaut 0, 1, 2, 3, 4 (5 valeurs) avant que la condition i < 5 devienne fausse.",
        },
        {
            "id": 6, "type": "single",
            "question": "Quel est le risque principal d'une boucle while mal écrite ?",
            "options": [
                "Elle s'exécute trop vite",
                "Elle ne s'exécute jamais",
                "Une boucle infinie si la condition ne devient jamais fausse",
                "Elle ne peut pas contenir de console.log",
            ],
            "correct_answer": 2,
            "explanation": "Si rien dans la boucle ne fait évoluer la condition vers false, elle tourne indéfiniment.",
        },
        {
            "id": 7, "type": "single",
            "question": "Que fait le mot-clé return dans une fonction ?",
            "options": [
                "Il affiche une valeur dans la console",
                "Il arrête la fonction et renvoie une valeur à l'appelant",
                "Il déclare une nouvelle variable",
                "Il ne fait rien de particulier",
            ],
            "correct_answer": 1,
            "explanation": "return arrête immédiatement l'exécution de la fonction et renvoie la valeur indiquée.",
        },
        {
            "id": 8, "type": "single",
            "question": "Que vaut le résultat d'une fonction qui ne contient aucun return ?",
            "options": ["null", "0", "undefined", "Une erreur est levée"],
            "correct_answer": 2,
            "explanation": "Sans return explicite, une fonction JavaScript renvoie undefined.",
        },
        {
            "id": 9, "type": "single",
            "question": "Quelle est l'écriture d'une fonction fléchée équivalente à function add(a, b) { return a + b; } ?",
            "options": [
                "const add = (a, b) => a + b;",
                "const add = function => a + b;",
                "arrow add(a, b) { return a + b; }",
                "const add = (a, b) -> a + b;",
            ],
            "correct_answer": 0,
            "explanation": "La syntaxe fléchée est (paramètres) => expression, sans le mot-clé function.",
        },
        {
            "id": 10, "type": "single",
            "question": "Dans un tableau const fruits = [\"Pomme\", \"Banane\"], quel est l'index du premier élément ?",
            "options": ["1", "0", "-1", "Cela dépend du tableau"],
            "correct_answer": 1,
            "explanation": "Les tableaux JavaScript sont indexés à partir de 0.",
        },
        {
            "id": 11, "type": "single",
            "question": "Que fait tableau.push(valeur) ?",
            "options": [
                "Retire le dernier élément du tableau",
                "Ajoute un élément au début du tableau",
                "Ajoute un élément à la fin du tableau",
                "Trie le tableau",
            ],
            "correct_answer": 2,
            "explanation": "push() ajoute un élément à la fin du tableau et modifie le tableau existant.",
        },
        {
            "id": 12, "type": "single",
            "question": "Quelle propriété donne le nombre d'éléments d'un tableau ?",
            "options": ["tableau.size", "tableau.count", "tableau.length", "tableau.total"],
            "correct_answer": 2,
            "explanation": "length est la propriété standard pour connaître la taille d'un tableau (ou d'une chaîne).",
        },
        {
            "id": 13, "type": "single",
            "question": "Que fait document.querySelector('.carte') ?",
            "options": [
                "Il crée un nouvel élément avec la classe carte",
                "Il sélectionne le premier élément ayant la classe carte",
                "Il sélectionne tous les éléments ayant la classe carte",
                "Il supprime l'élément .carte",
            ],
            "correct_answer": 1,
            "explanation": "querySelector renvoie le PREMIER élément correspondant au sélecteur CSS donné.",
        },
        {
            "id": 14, "type": "single",
            "question": "Quelle propriété modifie le texte affiché à l'intérieur d'un élément ?",
            "options": ["element.value", "element.textContent", "element.class", "element.href"],
            "correct_answer": 1,
            "explanation": "textContent lit ou modifie le texte contenu dans un élément HTML.",
        },
        {
            "id": 15, "type": "single",
            "question": "Quelle méthode ajoute une classe CSS à un élément en JavaScript ?",
            "options": [
                "element.addClass('nom')",
                "element.class.add('nom')",
                "element.classList.add('nom')",
                "element.style.class = 'nom'",
            ],
            "correct_answer": 2,
            "explanation": "classList.add()/remove()/toggle() gèrent les classes CSS d'un élément.",
        },
        {
            "id": 16, "type": "single",
            "question": "À quoi sert addEventListener('click', fonction) ?",
            "options": [
                "Il exécute la fonction immédiatement",
                "Il exécute la fonction seulement quand l'élément est cliqué",
                "Il crée un nouvel élément cliquable",
                "Il supprime les autres écouteurs d'événements",
            ],
            "correct_answer": 1,
            "explanation": "La fonction callback n'est exécutée que lorsque l'événement (ici 'click') se produit réellement.",
        },
        {
            "id": 17, "type": "single",
            "question": "Pourquoi appelle-t-on event.preventDefault() sur la soumission d'un formulaire ?",
            "options": [
                "Pour valider automatiquement tous les champs",
                "Pour empêcher le rechargement de page par défaut du navigateur",
                "Pour supprimer le formulaire de la page",
                "Ce n'est jamais nécessaire",
            ],
            "correct_answer": 1,
            "explanation": "Sans preventDefault(), le navigateur recharge la page à la soumission, ce qui coupe l'exécution du JavaScript.",
        },
        {
            "id": 18, "type": "single",
            "question": "Quelle est la différence entre console.log() et return dans une fonction ?",
            "options": [
                "Il n'y a aucune différence",
                "console.log affiche une valeur, return la renvoie pour être réutilisée",
                "return affiche une valeur, console.log la renvoie",
                "console.log ne fonctionne que dans les boucles",
            ],
            "correct_answer": 1,
            "explanation": "console.log est un outil de débogage (affichage), return produit la vraie valeur de sortie de la fonction.",
        },
        {
            "id": 19, "type": "multiple",
            "question": "Lesquelles de ces valeurs sont des types de base en JavaScript ? (plusieurs réponses)",
            "options": ["number", "string", "boolean", "array"],
            "correct_answer": [0, 1, 2],
            "explanation": "number, string et boolean sont des types primitifs. Un tableau (array) est un objet, pas un type primitif.",
        },
        {
            "id": 20, "type": "single",
            "question": "Où JavaScript peut-il s'exécuter ?",
            "options": [
                "Uniquement dans le navigateur",
                "Uniquement côté serveur",
                "Dans le navigateur ET côté serveur (avec Node.js)",
                "Uniquement dans un terminal",
            ],
            "correct_answer": 2,
            "explanation": "JavaScript tourne dans le navigateur, mais aussi côté serveur grâce à Node.js (qui exécute d'ailleurs vos exercices sur cette plateforme).",
        },
    ]

    _original_questions = copy.deepcopy(quiz_questions)
    _rng = random.Random(7)
    quiz_questions = [reorder_question(copy.deepcopy(q), _rng) for q in quiz_questions]
    verify_unchanged(_original_questions, quiz_questions)

    quiz, _ = Quiz.objects.update_or_create(
        lesson=quiz_lesson,
        defaults={
            'instructions': "Testez vos connaissances sur les fondamentaux de JavaScript : variables, conditions, boucles, fonctions, tableaux, DOM et événements.",
            'questions': quiz_questions,
            'passing_score': 70,
            'time_limit': 20,
            'randomize_questions': False,
            'randomize_options': True,
            'max_attempts': 0,
        }
    )

    # Distribution des positions correctes (vérification anti-biais)
    counts = {}
    for q in quiz_questions:
        ca = q['correct_answer']
        for p in (ca if isinstance(ca, list) else [ca]):
            counts[p] = counts.get(p, 0) + 1
    print(f"✅ Quiz créé : {quiz.question_count} questions")
    print("Distribution des positions correctes:", counts)

    total_duration = sum(
        Lesson.objects.filter(chapter=chapter).values_list('estimated_duration', flat=True)
    )
    chapter.estimated_duration = total_duration
    chapter.save(update_fields=['estimated_duration'])

    print("\n" + "=" * 70)
    lessons = Lesson.objects.filter(chapter=chapter).order_by('order_index')
    print(f"✨ Chapitre '{chapter.title}' : {lessons.count()} leçons, {total_duration} min estimées\n")
    for lesson in lessons:
        print(f"  {lesson.order_index:>2}. [{lesson.lesson_type:<8}] {lesson.title}")
