"""
Tests de la gamification.

L'essentiel porte sur l'invariant central : **rien ne peut être validé ni
crédité deux fois**, quel que soit le nombre de fois où l'on rejoue l'action.
"""
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.courses.models import Chapter, Lesson
from apps.gamification.models import Badge, PointTransaction, UserBadge, UserStreak
from apps.gamification.services import (
    award_lesson_points,
    award_points,
    get_points,
    level_progress,
    sync_user_gamification,
    touch_streak,
)
from apps.progression.models import UserProgress

pytestmark = pytest.mark.django_db

# Mots de passe de test. Valeurs volontairement descriptives : elles ne
# ressemblent pas à un identifiant réel, ce qui évite de déclencher les
# détecteurs de secrets sur chaque nouveau test. Elles satisfont malgré tout
# les validateurs Django (longueur, non courant, non numérique).
TEST_PASSWORD = 'fixture-pwd-not-a-real-secret'


@pytest.fixture
def learner():
    return User.objects.create_user(
        email='eleve@example.com', password=TEST_PASSWORD, first_name='Eve'
    )


@pytest.fixture
def api(learner):
    """Client DRF authentifié (l'API n'accepte que JWT, pas la session)."""
    client = APIClient()
    client.force_authenticate(user=learner)
    return client


@pytest.fixture
def lesson():
    chapter = Chapter.objects.create(
        title='HTML', slug='html', description='…',
        estimated_duration=60, is_published=True,
    )
    return Lesson.objects.create(
        chapter=chapter, title='Balises', slug='balises',
        lesson_type='THEORY', points=25, is_published=True,
    )


@pytest.fixture
def first_step_badge():
    return Badge.objects.create(
        code='premier-pas', name='Premier pas', description='…', icon='🌱',
        rule_type=Badge.RuleType.LESSONS_COMPLETED, criteria={'count': 1},
        points_reward=10,
    )


# ---------------------------------------------------------------------------
# Points : idempotence par source
# ---------------------------------------------------------------------------

def test_award_points_credite_une_seule_fois(learner):
    _, created_first = award_points(
        learner, 50, PointTransaction.Reason.MANUAL, source_key='test:x'
    )
    _, created_again = award_points(
        learner, 50, PointTransaction.Reason.MANUAL, source_key='test:x'
    )

    assert created_first is True
    assert created_again is False
    assert get_points(learner) == 50
    assert PointTransaction.objects.filter(user=learner).count() == 1


def test_points_de_lecon_non_rejouables(learner, lesson):
    assert award_lesson_points(learner, lesson) == 25
    assert award_lesson_points(learner, lesson) == 0
    assert award_lesson_points(learner, lesson) == 0
    assert get_points(learner) == 25


def test_sources_distinctes_cumulent(learner):
    award_points(learner, 30, PointTransaction.Reason.MANUAL, source_key='a')
    award_points(learner, 20, PointTransaction.Reason.MANUAL, source_key='b')
    assert get_points(learner) == 50


def test_niveau_suit_les_points(learner):
    award_points(learner, 250, PointTransaction.Reason.MANUAL, source_key='a')
    learner.profile.refresh_from_db()
    assert learner.profile.level == 3
    assert level_progress(250) == {
        'level': 3, 'points_in_level': 50, 'points_for_next': 50,
        'level_size': 100, 'percent': 50,
    }


# ---------------------------------------------------------------------------
# Badges : attribution unique
# ---------------------------------------------------------------------------

def test_badge_attribue_une_seule_fois(learner, lesson, first_step_badge):
    UserProgress.objects.create(
        user=learner, lesson=lesson,
        status=UserProgress.ProgressStatus.COMPLETED,
        completed_at=timezone.now(),
    )

    first_run = sync_user_gamification(learner)
    second_run = sync_user_gamification(learner)
    third_run = sync_user_gamification(learner)

    assert [b.badge.code for b in first_run] == ['premier-pas']
    assert second_run == []
    assert third_run == []
    assert UserBadge.objects.filter(user=learner, badge=first_step_badge).count() == 1
    # La récompense du badge n'a été créditée qu'une fois.
    assert get_points(learner) == 10


def test_badge_non_atteint_nest_pas_attribue(learner, first_step_badge):
    assert sync_user_gamification(learner) == []
    assert UserBadge.objects.count() == 0


def test_badge_reste_acquis_meme_si_la_progression_disparait(learner, lesson, first_step_badge):
    progress = UserProgress.objects.create(
        user=learner, lesson=lesson,
        status=UserProgress.ProgressStatus.COMPLETED,
    )
    sync_user_gamification(learner)
    progress.delete()

    # Réévaluation : le badge acquis n'est ni retiré, ni re-crédité.
    assert sync_user_gamification(learner) == []
    assert UserBadge.objects.filter(user=learner).count() == 1
    assert get_points(learner) == 10


def test_badge_inactif_ignore(learner, lesson, first_step_badge):
    first_step_badge.is_active = False
    first_step_badge.save()
    UserProgress.objects.create(
        user=learner, lesson=lesson, status=UserProgress.ProgressStatus.COMPLETED
    )
    assert sync_user_gamification(learner) == []


def test_recompense_de_badge_peut_debloquer_un_badge_de_points(learner, lesson, first_step_badge):
    """La cascade est résolue en un seul appel, sans double crédit."""
    Badge.objects.create(
        code='cap-10', name='Cap 10', description='…',
        rule_type=Badge.RuleType.POINTS_TOTAL, criteria={'points': 10},
    )
    UserProgress.objects.create(
        user=learner, lesson=lesson, status=UserProgress.ProgressStatus.COMPLETED
    )

    earned = {b.badge.code for b in sync_user_gamification(learner)}
    assert earned == {'premier-pas', 'cap-10'}
    assert sync_user_gamification(learner) == []


# ---------------------------------------------------------------------------
# Série de jours : idempotence à la journée
# ---------------------------------------------------------------------------

def test_streak_ne_compte_quune_fois_par_jour(learner):
    touch_streak(learner)
    touch_streak(learner)
    touch_streak(learner)

    streak = UserStreak.objects.get(user=learner)
    assert streak.current_streak == 1


def test_streak_progresse_le_lendemain(learner):
    now = timezone.now()
    touch_streak(learner, when=now - timedelta(days=2))
    touch_streak(learner, when=now - timedelta(days=1))
    touch_streak(learner, when=now)

    streak = UserStreak.objects.get(user=learner)
    assert streak.current_streak == 3
    assert streak.longest_streak == 3


def test_streak_se_reinitialise_apres_une_coupure(learner):
    now = timezone.now()
    touch_streak(learner, when=now - timedelta(days=10))
    touch_streak(learner, when=now - timedelta(days=9))
    touch_streak(learner, when=now)

    streak = UserStreak.objects.get(user=learner)
    assert streak.current_streak == 1
    assert streak.longest_streak == 2  # le record ne régresse jamais


# ---------------------------------------------------------------------------
# API : les objectifs secrets ne fuitent pas
# ---------------------------------------------------------------------------

def test_api_masque_les_badges_secrets_non_obtenus(api):
    Badge.objects.create(
        code='oiseau-de-nuit', name='Oiseau de nuit',
        description='Cinq sessions nocturnes', icon='🦉',
        hint='Certains apprennent quand les autres dorment…',
        is_secret=True,
        rule_type=Badge.RuleType.NIGHT_OWL, criteria={'count': 5},
        points_reward=35,
    )

    response = api.get('/api/gamification/badges/')
    assert response.status_code == 200

    payload = response.json()['badges'][0]
    body = response.content.decode()

    assert payload['name'] == 'Objectif secret'
    assert payload['code'] is None
    assert payload['points_reward'] is None
    assert payload['description'] == 'Certains apprennent quand les autres dorment…'
    # Aucune trace du vrai badge dans la réponse brute.
    assert 'oiseau-de-nuit' not in body
    assert 'Cinq sessions nocturnes' not in body


def test_api_revele_le_badge_secret_une_fois_obtenu(api, learner):
    badge = Badge.objects.create(
        code='oiseau-de-nuit', name='Oiseau de nuit',
        description='Cinq sessions nocturnes', icon='🦉',
        hint='…', is_secret=True,
        rule_type=Badge.RuleType.NIGHT_OWL, criteria={'count': 5},
    )
    UserBadge.objects.create(user=learner, badge=badge)

    payload = api.get('/api/gamification/badges/').json()['badges'][0]
    assert payload['name'] == 'Oiseau de nuit'
    assert payload['description'] == 'Cinq sessions nocturnes'
    assert payload['is_earned'] is True


def test_mark_seen_ne_rejoue_pas_la_revelation(api, learner, lesson, first_step_badge):
    UserProgress.objects.create(
        user=learner, lesson=lesson, status=UserProgress.ProgressStatus.COMPLETED
    )
    sync_user_gamification(learner)

    assert len(api.get('/api/gamification/summary/').json()['unseen_badges']) == 1

    api.post('/api/gamification/badges/mark_seen/', {}, format='json')

    assert api.get('/api/gamification/summary/').json()['unseen_badges'] == []


# ---------------------------------------------------------------------------
# « Continuer l'apprentissage » : quelle leçon proposer
# ---------------------------------------------------------------------------

@pytest.fixture
def parcours():
    """Un chapitre de trois leçons publiées, dans l'ordre."""
    chapter = Chapter.objects.create(
        title='HTML', slug='html-parcours', description='…',
        estimated_duration=60, is_published=True, order_index=0,
    )
    return [
        Lesson.objects.create(
            chapter=chapter, title=f'Leçon {i}', slug=f'lecon-{i}',
            lesson_type='THEORY', points=10, is_published=True, order_index=i,
        )
        for i in range(3)
    ]


def test_propose_la_premiere_lecon_quand_rien_nest_commence(api, parcours):
    data = api.get('/api/progression/progress/next_lesson/').json()

    assert data['lesson']['slug'] == 'lecon-0'
    assert data['is_resuming'] is False
    assert data['chapter_progress'] == {'position': 1, 'total': 3, 'completed': 0}


def test_saute_les_lecons_deja_terminees(api, learner, parcours):
    UserProgress.objects.create(
        user=learner, lesson=parcours[0],
        status=UserProgress.ProgressStatus.COMPLETED,
    )

    data = api.get('/api/progression/progress/next_lesson/').json()

    assert data['lesson']['slug'] == 'lecon-1'
    assert data['chapter_progress']['completed'] == 1


def test_comble_le_premier_trou_avant_la_lecon_entamee_plus_loin(api, learner, parcours):
    """⚠️ Règle inversée le 2026-08-06, volontairement.

    Ce test exigeait l'inverse : « continuer » ramenait à la leçon entamée la
    plus récente, où qu'elle soit dans le parcours. Constaté en usage réel : un
    compte ayant ouvert une leçon du dernier chapitre — ce que fait tout auteur
    ou formateur qui relit son contenu — se voyait proposer « Mettre son site
    en ligne » avec un chapitre 1 intact.

    « Où l'on en était » ne peut pas être plus loin que le premier trou du
    parcours : c'est ce trou qu'il faut combler d'abord. `is_resuming` dit
    seulement si la leçon proposée était déjà entamée.
    """
    UserProgress.objects.create(
        user=learner, lesson=parcours[2],
        status=UserProgress.ProgressStatus.IN_PROGRESS,
    )

    data = api.get('/api/progression/progress/next_lesson/').json()

    assert data['lesson']['slug'] == 'lecon-0'
    assert data['is_resuming'] is False


def test_signale_un_parcours_entierement_termine(api, learner, parcours):
    for lesson in parcours:
        UserProgress.objects.create(
            user=learner, lesson=lesson,
            status=UserProgress.ProgressStatus.COMPLETED,
        )

    data = api.get('/api/progression/progress/next_lesson/').json()

    assert data['lesson'] is None
    assert data['all_completed'] is True


def test_ignore_les_lecons_non_publiees(api, parcours):
    parcours[0].is_published = False
    parcours[0].save()

    data = api.get('/api/progression/progress/next_lesson/').json()

    assert data['lesson']['slug'] == 'lecon-1'
    assert data['chapter_progress']['total'] == 2


def test_sans_contenu_publie_aucune_lecon_nest_proposee(api):
    data = api.get('/api/progression/progress/next_lesson/').json()

    assert data['lesson'] is None
    assert data['all_completed'] is False


# ---------------------------------------------------------------------------
# Temps d'apprentissage
# ---------------------------------------------------------------------------

def test_le_temps_saccumule_au_lieu_de_secraser(api, learner, lesson):
    """Le suivi envoie des incréments : deux onglets s'additionnent."""
    for _ in range(3):
        response = api.post(
            '/api/progression/progress/track_time/',
            {'lesson_id': str(lesson.id), 'seconds': 30}, format='json'
        )
        assert response.status_code == 200

    progress = UserProgress.objects.get(user=learner, lesson=lesson)
    assert progress.time_spent == 90
    assert progress.status == UserProgress.ProgressStatus.IN_PROGRESS


def test_increment_de_temps_plafonne(api, learner, lesson):
    """Une valeur aberrante ne peut pas débloquer un badge de temps."""
    api.post(
        '/api/progression/progress/track_time/',
        {'lesson_id': str(lesson.id), 'seconds': 999_999}, format='json'
    )

    progress = UserProgress.objects.get(user=learner, lesson=lesson)
    assert progress.time_spent == 120  # MAX_TIME_INCREMENT_SECONDS


def test_increment_de_temps_invalide_refuse(api, lesson):
    for payload in (
        {'lesson_id': str(lesson.id), 'seconds': 0},
        {'lesson_id': str(lesson.id), 'seconds': -60},
        {'lesson_id': str(lesson.id), 'seconds': 'beaucoup'},
        {'seconds': 30},
    ):
        response = api.post(
            '/api/progression/progress/track_time/', payload, format='json'
        )
        assert response.status_code == 400, payload


def test_le_temps_ne_retrograde_pas_une_lecon_terminee(api, learner, lesson):
    UserProgress.objects.create(
        user=learner, lesson=lesson,
        status=UserProgress.ProgressStatus.COMPLETED,
        completed_at=timezone.now(),
    )

    api.post(
        '/api/progression/progress/track_time/',
        {'lesson_id': str(lesson.id), 'seconds': 45}, format='json'
    )

    progress = UserProgress.objects.get(user=learner, lesson=lesson)
    assert progress.status == UserProgress.ProgressStatus.COMPLETED
    assert progress.time_spent == 45


def test_le_temps_alimente_le_badge_de_duree(api, learner, lesson):
    Badge.objects.create(
        code='deux-minutes', name='Deux minutes', description='…',
        rule_type=Badge.RuleType.TIME_SPENT, criteria={'minutes': 2},
    )

    api.post(
        '/api/progression/progress/track_time/',
        {'lesson_id': str(lesson.id), 'seconds': 120}, format='json'
    )

    earned = {b.badge.code for b in sync_user_gamification(learner)}
    assert 'deux-minutes' in earned


def test_le_temps_passe_entretient_la_serie(api, learner, lesson):
    """Lire une leçon compte comme activité, pas seulement la terminer."""
    assert UserStreak.objects.filter(user=learner).count() == 0

    api.post(
        '/api/progression/progress/track_time/',
        {'lesson_id': str(lesson.id), 'seconds': 30}, format='json'
    )

    assert UserStreak.objects.get(user=learner).current_streak == 1


def test_time_spent_nest_pas_modifiable_en_valeur_absolue(api, learner, lesson):
    """Le PATCH ne doit pas offrir un contournement du plafond."""
    progress = UserProgress.objects.create(user=learner, lesson=lesson, time_spent=10)

    response = api.patch(
        f'/api/progression/progress/{progress.id}/',
        {'time_spent': 999_999}, format='json'
    )

    assert response.status_code == 200
    progress.refresh_from_db()
    assert progress.time_spent == 10


def test_marquer_la_lecon_terminee_deux_fois_ne_double_pas_les_points(api, learner, lesson):
    """Le parcours HTTP complet respecte lui aussi l'invariant."""
    first = api.post(
        '/api/progression/progress/mark_completed/',
        {'lesson_id': str(lesson.id)}, format='json'
    ).json()
    second = api.post(
        '/api/progression/progress/mark_completed/',
        {'lesson_id': str(lesson.id)}, format='json'
    ).json()

    assert first['points_earned'] == 25
    assert second['points_earned'] == 0
    assert second['total_points'] == 25
    assert second['new_badges'] == []


# ---------------------------------------------------------------------------
# Catalogue de badges
#
# `seed_badges` est du contenu, pas de la logique — mais deux de ses propriétés
# se cassent en silence, et ce sont celles-là qu'on verrouille : un badge qui
# vise un chapitre inexistant reste éternellement à 0 sans rien signaler, et
# un code en double ferait échouer le semis à la première contrainte d'unicité.
# ---------------------------------------------------------------------------

def test_les_badges_de_chapitre_visent_un_slug_reellement_charge():
    """Un `chapter_slug` erroné donne un badge inatteignable et muet.

    C'est le seul défaut du catalogue qui ne se voit ni au semis, ni à la
    lecture de l'API : la règle renvoie « 0 sur 1 », pour toujours.

    ⚠️ Le test lit les **sources des commandes de chargement**, et non la base
    de test. Peupler la base ici ne vérifierait que la cohérence du test avec
    lui-même ; c'est le lien entre `seed_badges` et `load_section_*` qui doit
    tenir, donc c'est lui qu'on interroge. Renommer un chapitre dans un
    chargeur fait désormais rougir ce test.
    """
    from pathlib import Path

    from apps.courses.management.commands import load_course_content
    from apps.gamification.management.commands.seed_badges import VISIBLE, SECRET

    vises = {
        badge['criteria']['chapter_slug']
        for badge in VISIBLE + SECRET
        if badge['rule_type'] == Badge.RuleType.CHAPTER_MASTERED
    }
    assert vises, 'Aucun badge de chapitre : le test ne protège plus rien.'

    dossier = Path(load_course_content.__file__).parent
    sources = '\n'.join(
        fichier.read_text(encoding='utf-8')
        for fichier in dossier.glob('load_section_*.py')
    )

    introuvables = sorted(slug for slug in vises if f"'{slug}'" not in sources)
    assert not introuvables, (
        f'Slugs cités par un badge mais absents des chargeurs : {introuvables}'
    )


def test_les_codes_de_badge_sont_uniques():
    """`code` porte une contrainte d'unicité **et** sert de clé au grand livre
    (`badge:<code>`). Un doublon casserait le semis et fausserait les points."""
    from apps.gamification.management.commands.seed_badges import VISIBLE, SECRET

    codes = [badge['code'] for badge in VISIBLE + SECRET]
    assert len(codes) == len(set(codes))


def test_seul_le_catalogue_secret_porte_une_enigme():
    """`is_secret` est déduit de la présence d'un `hint` (cf. `handle`).

    Un badge secret sans énigme sortirait de l'API entièrement masqué, sans
    rien à afficher — une case vide que personne ne peut résoudre. Un badge
    visible *avec* énigme, lui, serait rangé du mauvais côté.
    """
    from apps.gamification.management.commands.seed_badges import VISIBLE, SECRET

    assert all('hint' not in badge for badge in VISIBLE)
    assert all(badge.get('hint') for badge in SECRET)
