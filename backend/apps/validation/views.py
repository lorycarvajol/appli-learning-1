"""
Views pour l'app validation
"""

from celery.result import AsyncResult
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.courses.models import Exercise
from .serializers import CodeSubmissionSerializer, ValidationResultSerializer
from .tasks import run_code_validation


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_exercise_code(request, exercise_id):
    """
    Soumet du code pour un exercice. La validation s'exécute de façon
    asynchrone dans un worker Celery dédié (queue "validation") pour ne
    pas bloquer les workers web pendant l'exécution du sandbox Docker.

    POST /api/validation/exercises/<exercise_id>/submit/
    Body: { "code": "..." }

    Returns 202: { "task_id": "...", "status": "PENDING" }
    Le résultat final s'obtient en interrogeant
    GET /api/validation/tasks/<task_id>/
    """
    exercise = get_object_or_404(Exercise, id=exercise_id)

    submission_serializer = CodeSubmissionSerializer(data=request.data)
    if not submission_serializer.is_valid():
        return Response(
            submission_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    user_code = submission_serializer.validated_data['code']

    task = run_code_validation.apply_async(args=[str(exercise.id), user_code])

    return Response(
        {'task_id': task.id, 'status': 'PENDING'},
        status=status.HTTP_202_ACCEPTED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_validation_result(request, task_id):
    """
    Interroge le résultat d'une validation de code soumise précédemment.

    GET /api/validation/tasks/<task_id>/

    Returns:
        202 { "status": "PENDING" }             tant que le worker traite la tâche
        200 { ...ValidationResultSerializer }    une fois le résultat disponible
        500 { "status": "FAILURE", "error": "" } en cas d'erreur worker inattendue
    """
    result = AsyncResult(task_id)

    if result.state in ('PENDING', 'STARTED', 'RETRY'):
        return Response({'status': 'PENDING'}, status=status.HTTP_202_ACCEPTED)

    if result.state == 'FAILURE':
        return Response(
            {
                'status': 'FAILURE',
                'success': False,
                'error': 'Une erreur est survenue lors de la validation',
                'results': [],
                'total_points': 0,
                'max_points': 0,
                'message': '❌ Une erreur est survenue lors de la validation',
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # SUCCESS : le résultat a déjà été enrichi du message pédagogique dans la tâche
    payload = result.result
    result_serializer = ValidationResultSerializer(data=payload)
    if result_serializer.is_valid():
        return Response(result_serializer.data, status=status.HTTP_200_OK)
    return Response(payload, status=status.HTTP_200_OK)
