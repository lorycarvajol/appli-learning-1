"""
URL configuration for courses API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChapterViewSet, LessonViewSet, ExerciseViewSet,
    QuizViewSet, ProjectViewSet
)

app_name = 'courses'

router = DefaultRouter()
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'exercises', ExerciseViewSet, basename='exercise')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'projects', ProjectViewSet, basename='project')

urlpatterns = [
    path('', include(router.urls)),
]
