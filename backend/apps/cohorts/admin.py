from django.contrib import admin
from django.utils.html import format_html

from .models import Cohort, CohortInvite
from .services import build_invite_url


class CohortInviteInline(admin.TabularInline):
    model = CohortInvite
    extra = 0
    fields = ['token', 'role', 'expires_at', 'max_uses', 'uses_count', 'is_revoked']
    readonly_fields = ['token', 'uses_count']


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ['name', 'trainer', 'member_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'trainer']
    search_fields = ['name', 'trainer__email']
    inlines = [CohortInviteInline]

    @admin.display(description='Membres')
    def member_count(self, cohort):
        return cohort.member_count


@admin.register(CohortInvite)
class CohortInviteAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'role', 'state', 'uses_count', 'max_uses', 'expires_at']
    list_filter = ['role', 'is_revoked', 'cohort']
    search_fields = ['token', 'cohort__name']
    readonly_fields = ['token', 'uses_count', 'created_at', 'link']

    @admin.display(description='État')
    def state(self, invite):
        reason = invite.invalid_reason()
        return 'utilisable' if reason is None else reason

    @admin.display(description='Lien à diffuser')
    def link(self, invite):
        if not invite.pk:
            return '—'
        url = build_invite_url(invite)
        return format_html('<code>{}</code>', url)
