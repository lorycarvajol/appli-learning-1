"""
Tâches Celery pour l'app validation.

L'exécution Docker est déportée ici (worker Celery dédié à la queue
"validation") plutôt que dans le worker web Gunicorn qui traite la requête
HTTP : ça libère les workers web immédiatement et confine l'accès au socket
Docker au conteneur Celery.
"""

from celery import shared_task

from .services import validate_exercise_code


def _build_pedagogical_message(result):
    """Ajoute un message pédagogique au résultat selon le taux de réussite."""
    if result.get('success'):
        result['message'] = '🎉 Bravo ! Tous les tests sont passés. Vous maîtrisez cette notion !'
        return result

    if result.get('error'):
        result['message'] = f"❌ {result['error']}"
        return result

    passed_count = sum(1 for r in result.get('results', []) if r.get('passed'))
    total_count = len(result.get('results', []))
    failed_count = total_count - passed_count
    percentage = (passed_count / total_count * 100) if total_count > 0 else 0

    if percentage >= 80:
        result['message'] = f'💪 Presque parfait ! {passed_count}/{total_count} tests réussis. Plus que {failed_count} test(s) à corriger !'
    elif percentage >= 50:
        result['message'] = f'👍 Bon travail ! {passed_count}/{total_count} tests réussis. Consultez les messages d\'erreur ci-dessous pour corriger les {failed_count} test(s) restant(s).'
    elif percentage >= 25:
        result['message'] = f'📚 Vous progressez ! {passed_count}/{total_count} tests réussis. Lisez attentivement les instructions pour les {failed_count} test(s) échoué(s).'
    else:
        result['message'] = f'🎯 Bon départ ! {passed_count}/{total_count} tests réussis. Relisez les instructions de l\'exercice et vérifiez votre code étape par étape.'

    return result


@shared_task(bind=True, queue='validation', name='validation.run_code_validation')
def run_code_validation(self, exercise_id, user_code):
    """
    Exécute la validation Docker d'une soumission d'exercice.

    Args:
        exercise_id: UUID (str) de l'exercice
        user_code: code soumis par l'apprenant

    Returns:
        dict sérialisable prêt à être renvoyé tel quel par l'API
        (mêmes clés que l'ancien flux synchrone : success, results,
        total_points, max_points, error, message).
    """
    from apps.courses.models import Exercise

    try:
        exercise = Exercise.objects.get(id=exercise_id)
    except Exercise.DoesNotExist:
        return {
            'success': False,
            'error': 'Exercice introuvable',
            'results': [],
            'total_points': 0,
            'max_points': 0,
            'message': '❌ Cet exercice n\'existe plus',
        }

    try:
        result = validate_exercise_code(exercise, user_code)
    except Exception as e:
        result = {
            'success': False,
            'error': f'Erreur lors de la validation: {str(e)}',
            'results': [],
            'total_points': 0,
            'max_points': 0,
        }

    return _build_pedagogical_message(result)
