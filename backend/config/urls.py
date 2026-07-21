"""
URL configuration for learning platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.utils.html import format_html

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/courses/', include('apps.courses.urls')),
    path('api/progression/', include('apps.progression.urls')),
    path('api/validation/', include('apps.validation.urls')),
    path('api/gamification/', include('apps.gamification.urls')),
    path('api/cohorts/', include('apps.cohorts.urls')),
    path('api/administration/', include('apps.administration.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]

# Personnalisation de l'admin Django.
#
# Le titre dit explicitement le partage des rôles : cet espace sert au contenu
# pédagogique, le pilotage se fait dans l'espace React. Sans ce rappel, un
# administrateur qui arrive ici cherche à changer un rôle depuis le formulaire
# `User` — où les champs sont désormais en lecture seule — sans comprendre
# pourquoi ça ne marche pas.
admin.site.site_header = "Plateforme d'apprentissage — contenu"
admin.site.site_title = "Administration du contenu"
admin.site.index_title = format_html(
    'Chapitres, leçons, exercices, quiz et badges. '
    'Le pilotage (comptes, rôles, classes, journal d’audit) se fait dans '
    '<a href="{}/administration">l’espace Administration</a>.',
    settings.FRONTEND_URL.rstrip('/'),
)
