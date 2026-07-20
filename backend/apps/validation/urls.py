"""
URLs pour l'app validation
"""

from django.urls import path
from . import views

app_name = 'validation'

urlpatterns = [
    path(
        'exercises/<uuid:exercise_id>/submit/',
        views.submit_exercise_code,
        name='submit-exercise-code'
    ),
    path(
        'tasks/<str:task_id>/',
        views.get_validation_result,
        name='validation-task-result'
    ),
]
