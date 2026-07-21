"""
Corrige le biais de position des réponses du quiz HTML
("Quiz : Les Fondamentaux du HTML") : la bonne réponse était en position 1
pour 16 des 20 questions. Ce script mélange l'ordre des options de chaque
question (le contenu et la réponse correcte restent inchangés, seule leur
position dans la liste change) et active le mélange à l'affichage.
"""

import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.courses.models import Lesson


def reorder_question(question, rng):
    options = question['options']
    n = len(options)
    permutation = list(range(n))
    rng.shuffle(permutation)

    new_options = [options[i] for i in permutation]
    # position_map[old_index] = new_index
    position_map = {old: new for new, old in enumerate(permutation)}

    old_correct = question['correct_answer']
    if isinstance(old_correct, list):
        new_correct = sorted(position_map[i] for i in old_correct)
    else:
        new_correct = position_map[old_correct]

    question['options'] = new_options
    question['correct_answer'] = new_correct
    return question


def verify(original_questions, fixed_questions):
    """Vérifie que le texte des bonnes réponses n'a pas changé, seulement leur position."""
    for orig, fixed in zip(original_questions, fixed_questions):
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

        assert orig_texts == fixed_texts, f"MISMATCH on question {orig['id']}: {orig_texts} != {fixed_texts}"
        assert set(orig['options']) == set(fixed['options']), f"Options changed on question {orig['id']}"


if __name__ == '__main__':
    lesson = Lesson.objects.get(slug='quiz-html-fondamentaux')
    quiz = lesson.quiz

    original = quiz.questions if isinstance(quiz.questions, list) else quiz.questions.get('questions', [])
    import copy
    original_copy = copy.deepcopy(original)

    rng = random.Random(42)
    fixed = [reorder_question(copy.deepcopy(q), rng) for q in original]

    verify(original_copy, fixed)

    quiz.questions = fixed
    quiz.randomize_options = True
    quiz.save(update_fields=['questions', 'randomize_options'])

    counts = {}
    for q in fixed:
        ca = q['correct_answer']
        positions = ca if isinstance(ca, list) else [ca]
        for p in positions:
            counts[p] = counts.get(p, 0) + 1

    print('✅ Options réordonnées et vérifiées (contenu inchangé).')
    print('✅ randomize_options activé.')
    print('Nouvelle distribution des positions correctes:', counts)
