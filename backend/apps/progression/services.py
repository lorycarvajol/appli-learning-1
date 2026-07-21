"""
Accès aux chapitres.

Deux régimes coexistent, décidés par l'appartenance à une classe :

- **En classe** : le formateur donne le tempo. Un chapitre n'est accessible que
  s'il a été explicitement débloqué (`ChapterAccess.is_unlocked`).
- **En autonomie** (aucune classe) : rythme libre. Le premier chapitre est
  ouvert, et le suivant s'ouvre dès que le précédent est entièrement terminé.
  Sans cette règle, un apprenant inscrit librement n'aurait personne pour lui
  débloquer quoi que ce soit et resterait devant un parcours mort.

Règle transverse : **on ne reverrouille jamais**. Un accès obtenu le reste,
qu'on rejoigne une classe ensuite ou qu'on quitte la sienne. C'est la même
logique de monotonie que pour les badges — elle rend les recalculs sûrs.
"""
from django.db import transaction
from django.utils import timezone

from apps.courses.models import Chapter

from .models import ChapterAccess, UserProgress

STAFF_ROLES = ('TRAINER', 'ADMIN')


def has_staff_role(user):
    """Teste le **rôle**, pas le champ Django `is_staff`.

    Nommée `is_staff_user` à l'origine, ce qui laissait croire qu'elle lisait
    `user.is_staff` — deux notions distinctes à l'époque.
    """
    return bool(user) and getattr(user, 'role', None) in STAFF_ROLES


def _completed_chapter_ids(user, chapters):
    """Chapitres dont *toutes* les leçons publiées sont terminées."""
    completed_lesson_ids = set(
        UserProgress.objects.filter(
            user=user, status=UserProgress.ProgressStatus.COMPLETED
        ).values_list('lesson_id', flat=True)
    )

    done = set()
    for chapter in chapters:
        lesson_ids = [l.id for l in chapter.lessons.all() if l.is_published]
        if lesson_ids and all(lid in completed_lesson_ids for lid in lesson_ids):
            done.add(chapter.id)
    return done


def ensure_self_paced_access(user):
    """Ouvre les chapitres dus à un apprenant autonome.

    Idempotent : les accès sont matérialisés avec `get_or_create` et jamais
    retirés. Les matérialiser plutôt que de les calculer à la volée garde
    l'état visible dans l'admin et dans le tableau de bord formateur.

    Ne fait rien pour un apprenant rattaché à une classe : c'est son formateur
    qui décide.
    """
    if has_staff_role(user):
        return []

    profile = getattr(user, 'profile', None)
    if profile is None or profile.cohort_id is not None:
        return []

    chapters = list(
        Chapter.objects.filter(is_published=True)
        .order_by('order_index')
        .prefetch_related('lessons')
    )
    if not chapters:
        return []

    completed = _completed_chapter_ids(user, chapters)
    already_unlocked = set(
        ChapterAccess.objects.filter(user=user, is_unlocked=True)
        .values_list('chapter_id', flat=True)
    )

    newly_unlocked = []
    for index, chapter in enumerate(chapters):
        # Le premier chapitre est toujours ouvert ; les suivants attendent que
        # le précédent soit bouclé.
        earned = index == 0 or chapters[index - 1].id in completed
        if not earned or chapter.id in already_unlocked:
            continue

        access, created = ChapterAccess.objects.get_or_create(
            user=user,
            chapter=chapter,
            defaults={'is_unlocked': True, 'unlocked_at': timezone.now()},
        )
        if not created and not access.is_unlocked:
            access.is_unlocked = True
            access.unlocked_at = timezone.now()
            access.save(update_fields=['is_unlocked', 'unlocked_at', 'updated_at'])

        newly_unlocked.append(chapter)

    return newly_unlocked


def accessible_chapter_ids(user):
    """Ensemble des ids de chapitres que cet utilisateur peut ouvrir."""
    if has_staff_role(user):
        return set(
            Chapter.objects.filter(is_published=True).values_list('id', flat=True)
        )

    ensure_self_paced_access(user)

    return set(
        ChapterAccess.objects.filter(user=user, is_unlocked=True)
        .values_list('chapter_id', flat=True)
    )


def can_access_chapter(user, chapter):
    if has_staff_role(user):
        return True
    ensure_self_paced_access(user)
    return ChapterAccess.objects.filter(
        user=user, chapter=chapter, is_unlocked=True
    ).exists()


def can_access_lesson(user, lesson):
    return can_access_chapter(user, lesson.chapter)


def unlock_chapter_for(user, chapter, unlocked_by=None):
    """Débloque un chapitre pour un apprenant. Idempotent."""
    with transaction.atomic():
        access, created = ChapterAccess.objects.get_or_create(
            user=user,
            chapter=chapter,
            defaults={
                'is_unlocked': True,
                'unlocked_by': unlocked_by,
                'unlocked_at': timezone.now(),
            },
        )
        if not created and not access.is_unlocked:
            access.is_unlocked = True
            access.unlocked_by = unlocked_by
            access.unlocked_at = timezone.now()
            access.save()
            created = True  # au sens « l'accès vient d'être ouvert »
    return access, created
