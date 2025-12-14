"""
Views pour l'app validation
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.courses.models import Exercise
from .serializers import CodeSubmissionSerializer, ValidationResultSerializer
from .services import validate_exercise_code


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_exercise_code(request, exercise_id):
    """
    Soumet du code pour un exercice et retourne les résultats de validation

    POST /api/validation/exercises/<exercise_id>/submit/
    Body: { "code": "..." }

    Returns:
        {
            "success": true/false,
            "results": [
                {
                    "name": "Test name",
                    "passed": true/false,
                    "points": 10,
                    "message": "..."
                }
            ],
            "total_points": 20,
            "max_points": 30,
            "error": null,
            "message": "..."
        }
    """
    # Récupérer l'exercice
    exercise = get_object_or_404(Exercise, id=exercise_id)

    # Valider la soumission
    submission_serializer = CodeSubmissionSerializer(data=request.data)
    if not submission_serializer.is_valid():
        return Response(
            submission_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # Récupérer le code soumis
    user_code = submission_serializer.validated_data['code']

    try:
        # Valider le code avec le sandbox Docker
        result = validate_exercise_code(exercise, user_code)

        # Ajouter un message global pédagogique
        if result.get('success'):
            result['message'] = '🎉 Bravo ! Tous les tests sont passés. Vous maîtrisez cette notion !'
        else:
            if result.get('error'):
                result['message'] = f"❌ {result['error']}"
            else:
                passed_count = sum(1 for r in result.get('results', []) if r.get('passed'))
                total_count = len(result.get('results', []))
                failed_count = total_count - passed_count
                percentage = (passed_count / total_count * 100) if total_count > 0 else 0

                # Message encourageant selon le pourcentage de réussite
                if percentage >= 80:
                    result['message'] = f'💪 Presque parfait ! {passed_count}/{total_count} tests réussis. Plus que {failed_count} test(s) à corriger !'
                elif percentage >= 50:
                    result['message'] = f'👍 Bon travail ! {passed_count}/{total_count} tests réussis. Consultez les messages d\'erreur ci-dessous pour corriger les {failed_count} test(s) restant(s).'
                elif percentage >= 25:
                    result['message'] = f'📚 Vous progressez ! {passed_count}/{total_count} tests réussis. Lisez attentivement les instructions pour les {failed_count} test(s) échoué(s).'
                else:
                    result['message'] = f'🎯 Bon départ ! {passed_count}/{total_count} tests réussis. Relisez les instructions de l\'exercice et vérifiez votre code étape par étape.'

        # Sérializer le résultat
        result_serializer = ValidationResultSerializer(data=result)
        if result_serializer.is_valid():
            return Response(result_serializer.data, status=status.HTTP_200_OK)
        else:
            # Si le résultat ne peut pas être sérialisé, retourner quand même
            return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {
                'success': False,
                'error': f'Erreur lors de la validation: {str(e)}',
                'results': [],
                'total_points': 0,
                'max_points': 0,
                'message': '❌ Une erreur est survenue lors de la validation'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
