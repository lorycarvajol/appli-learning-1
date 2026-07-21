"""
Admin Django des classes — réduit à ce que React ne couvre pas.

L'espace React et l'espace formateur gèrent déjà la création d'une classe,
l'affectation du formateur, les membres et les invitations. Ne restent ici que
le **renommage**, la **description** et l'**archivage**, sans équivalent côté
React. Voir `apps/administration/admin_readonly.py`.
"""
from django.contrib import admin
from django.utils.html import format_html

from apps.administration.admin_readonly import ReadOnlyAdmin

from .models import Cohort, CohortInvite
from .services import build_invite_url


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ['name', 'trainer', 'member_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'trainer']
    search_fields = ['name', 'trainer__email']
    fields = ['name', 'description', 'is_active', 'trainer']

    #: L'affectation passe par `POST /cohorts/<id>/set_trainer/`, réservé aux
    #: admins et journalisé. La modifier ici contournerait les deux : pas de
    #: trace, et aucune vérification que le compte visé est bien formateur —
    #: confier une classe à un apprenant lui donnerait vue sur ses camarades.
    readonly_fields = ['trainer']

    @admin.display(description='Membres')
    def member_count(self, cohort):
        return cohort.member_count

    def has_delete_permission(self, request, obj=None):
        """Supprimer une classe détache ses apprenants en silence.

        Ils redeviendraient autonomes sans que personne en soit informé.
        Archiver (`is_active`) exprime la même intention de façon réversible.
        """
        return False


@admin.register(CohortInvite)
class CohortInviteAdmin(ReadOnlyAdmin):
    """Lecture seule : émettre une invitation est un acte, pas une saisie.

    L'API applique une règle que ce formulaire ignorait : **seul un admin peut
    émettre une invitation de rôle TRAINER**, sans quoi le rôle formateur
    s'auto-réplique. Elle journalise aussi l'émission et la révocation.

    Les liens restent affichés — le formateur doit pouvoir recopier le sien,
    c'est la raison pour laquelle le jeton est stocké en clair.
    """

    list_display = ['__str__', 'role', 'state', 'uses_count', 'max_uses', 'expires_at']
    list_filter = ['role', 'is_revoked', 'cohort']
    search_fields = ['token', 'cohort__name']

    def get_readonly_fields(self, request, obj=None):
        return [*super().get_readonly_fields(request, obj), 'link']

    @admin.display(description='État')
    def state(self, invite):
        reason = invite.invalid_reason()
        return 'utilisable' if reason is None else reason

    @admin.display(description='Lien à diffuser')
    def link(self, invite):
        if not invite.pk:
            return '—'
        return format_html('<code>{}</code>', build_invite_url(invite))
