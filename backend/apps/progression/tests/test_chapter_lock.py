"""
Tests du verrou de chapitre — la « progression contrôlée par le formateur ».

Cette promesse a longtemps été **décorative** : `ChapterAccess` existait, mais
aucune vue apprenant ne le consultait. L'API cours ne filtrait rien. Le verrou
n'est devenu réel qu'en posant le contrôle dans `LessonViewSet.retrieve`, et
il n'avait jusqu'ici aucun test.

Deux régimes coexistent, et la confusion entre les deux est la faute la plus
facile à commettre :

| Situation | Qui ouvre les chapitres |
|---|---|
| Apprenant **en classe** | Le formateur, explicitement |
| Apprenant **autonome** | Rythme libre : le N+1 s'ouvre quand le N est fini |
"""
import pytest

from apps.accounts.models import User
from apps.progression.models import ChapterAccess, UserProgress
from apps.progression.services import (
    accessible_chapter_ids,
    can_access_chapter,
    cohort_unlocked_chapter_ids,
    unlock_chapter_for,
)

from .conftest import TEST_PASSWORD

pytestmark = pytest.mark.django_db


def terminer_chapitre(user, chapter):
    """Marque toutes les leçons publiées d'un chapitre comme terminées."""
    for lesson in chapter.lessons.filter(is_published=True):
        UserProgress.objects.update_or_create(
            user=user, lesson=lesson,
            defaults={'status': UserProgress.ProgressStatus.COMPLETED},
        )


# ---------------------------------------------------------------------------
# « Ouvert à la classe » : le retour visuel du panneau formateur
# ---------------------------------------------------------------------------

def test_chapitre_ouvert_a_la_classe_seulement_si_tous_les_membres_l_ont(
    cohort, cohort_learner, parcours
):
    """Vert uniquement quand *chaque* membre a l'accès — sinon le formateur
    croirait la classe entière servie alors qu'un apprenant est laissé dehors."""
    autre = User.objects.create_user(email='autre@example.com', password=TEST_PASSWORD)
    autre.profile.cohort = cohort_learner.profile.cohort
    autre.profile.save(update_fields=['cohort'])

    ch1 = parcours[0]

    unlock_chapter_for(cohort_learner, ch1)
    assert ch1.id not in cohort_unlocked_chapter_ids(cohort)  # un seul des deux

    unlock_chapter_for(autre, ch1)
    assert ch1.id in cohort_unlocked_chapter_ids(cohort)      # les deux


def test_classe_vide_n_a_aucun_chapitre_ouvert(cohort, parcours):
    assert cohort_unlocked_chapter_ids(cohort) == set()


# ---------------------------------------------------------------------------
# Le verrou mord réellement
# ---------------------------------------------------------------------------

def test_une_lecon_verrouillee_renvoie_403(client_for, cohort_learner, parcours):
    """Le cœur du dispositif. Sans ce refus, tout le reste est décoratif."""
    lecon = parcours[2].lessons.first()

    response = client_for(cohort_learner).get(f'/api/courses/lessons/{lecon.slug}/')

    assert response.status_code == 403
    assert response.data['chapter_slug'] == parcours[2].slug


def test_le_contenu_dune_lecon_verrouillee_nest_pas_servi(
    client_for, cohort_learner, parcours
):
    """Un 403 qui laisserait fuiter le contenu ne servirait à rien."""
    lecon = parcours[2].lessons.first()

    response = client_for(cohort_learner).get(f'/api/courses/lessons/{lecon.slug}/')

    assert 'content' not in response.data
    assert lecon.title not in str(response.data)


def test_les_chapitres_verrouilles_restent_listes(client_for, cohort_learner, parcours):
    """Choix délibéré : masquer la suite priverait l'apprenant de la vue
    d'ensemble qui lui donne envie d'avancer. C'est l'ouverture qui est
    bloquée, pas le sommaire."""
    response = client_for(cohort_learner).get('/api/courses/chapters/')

    resultats = response.data.get('results', response.data)
    assert len(resultats) == 3

    acces = {c['slug']: c['is_accessible'] for c in resultats}
    assert acces['chapitre-3'] is False


def test_un_formateur_ouvre_toutes_les_lecons(client_for, trainer, parcours):
    """L'encadrement doit pouvoir relire le contenu qu'il pilote."""
    lecon = parcours[2].lessons.first()

    assert client_for(trainer).get(
        f'/api/courses/lessons/{lecon.slug}/'
    ).status_code == 200


# ---------------------------------------------------------------------------
# Apprenant en classe : le formateur donne le tempo
# ---------------------------------------------------------------------------

def test_un_apprenant_en_classe_na_rien_douvert_au_depart(cohort_learner, parcours):
    """Aucun rythme libre : sans geste du formateur, rien ne s'ouvre — pas
    même le premier chapitre."""
    assert accessible_chapter_ids(cohort_learner) == set()


def test_le_deblocage_par_le_formateur_ouvre_la_lecon(
    client_for, cohort_learner, trainer, parcours
):
    unlock_chapter_for(cohort_learner, parcours[2], unlocked_by=trainer)

    lecon = parcours[2].lessons.first()
    assert client_for(cohort_learner).get(
        f'/api/courses/lessons/{lecon.slug}/'
    ).status_code == 200


def test_terminer_un_chapitre_nouvre_pas_le_suivant_en_classe(
    cohort_learner, trainer, parcours
):
    """La différence essentielle entre les deux régimes : en classe, finir ne
    donne aucun droit. Le formateur reste seul maître du tempo."""
    unlock_chapter_for(cohort_learner, parcours[0], unlocked_by=trainer)
    terminer_chapitre(cohort_learner, parcours[0])

    assert can_access_chapter(cohort_learner, parcours[1]) is False


# ---------------------------------------------------------------------------
# Apprenant autonome : rythme libre
# ---------------------------------------------------------------------------

def test_le_premier_chapitre_est_ouvert_a_un_autonome(learner, parcours):
    """Sinon un inscrit sans classe resterait bloqué à la porte, sans
    personne pour la lui ouvrir."""
    assert can_access_chapter(learner, parcours[0]) is True
    assert can_access_chapter(learner, parcours[1]) is False


def test_terminer_un_chapitre_ouvre_le_suivant(learner, parcours):
    terminer_chapitre(learner, parcours[0])

    assert can_access_chapter(learner, parcours[1]) is True
    # Mais pas au-delà : on avance d'un cran, pas de deux.
    assert can_access_chapter(learner, parcours[2]) is False


def test_un_chapitre_partiellement_fait_nouvre_pas_le_suivant(learner, parcours):
    """« Terminé » veut dire *toutes* les leçons publiées, pas la première."""
    premiere = parcours[0].lessons.first()
    UserProgress.objects.create(
        user=learner, lesson=premiere,
        status=UserProgress.ProgressStatus.COMPLETED,
    )

    assert can_access_chapter(learner, parcours[1]) is False


def test_louverture_automatique_est_idempotente(learner, parcours):
    """`ensure_self_paced_access` est appelée à chaque lecture d'accès : elle
    ne doit pas empiler les enregistrements."""
    terminer_chapitre(learner, parcours[0])

    for _ in range(3):
        accessible_chapter_ids(learner)

    assert ChapterAccess.objects.filter(user=learner).count() == 2


# ---------------------------------------------------------------------------
# On ne reverrouille jamais
# ---------------------------------------------------------------------------

def test_rejoindre_une_classe_ne_retire_pas_un_acces_acquis(
    learner, cohort, parcours
):
    """Règle de monotonie, comme pour les badges : un accès obtenu le reste.

    Sans elle, un apprenant qui avançait seul serait puni de rejoindre une
    classe — ses chapitres ouverts se refermeraient d'un coup.
    """
    terminer_chapitre(learner, parcours[0])
    assert can_access_chapter(learner, parcours[1]) is True

    learner.profile.cohort = cohort
    learner.profile.save(update_fields=['cohort'])

    assert can_access_chapter(learner, parcours[1]) is True


def test_quitter_une_classe_ne_retire_pas_un_acces_acquis(
    cohort_learner, trainer, parcours
):
    unlock_chapter_for(cohort_learner, parcours[2], unlocked_by=trainer)

    cohort_learner.profile.cohort = None
    cohort_learner.profile.save(update_fields=['cohort'])

    assert can_access_chapter(cohort_learner, parcours[2]) is True


def test_le_deblocage_est_idempotent(cohort_learner, trainer, parcours):
    for _ in range(3):
        unlock_chapter_for(cohort_learner, parcours[1], unlocked_by=trainer)

    assert ChapterAccess.objects.filter(
        user=cohort_learner, chapter=parcours[1]
    ).count() == 1


# ---------------------------------------------------------------------------
# Un chapitre non publié n'entre pas dans le calcul
# ---------------------------------------------------------------------------

def test_un_chapitre_non_publie_ne_bloque_pas_la_progression(learner, parcours):
    """Un brouillon inséré au milieu du parcours ne doit pas devenir un mur
    infranchissable : personne ne peut le terminer."""
    brouillon = parcours[1]
    brouillon.is_published = False
    brouillon.save(update_fields=['is_published'])

    terminer_chapitre(learner, parcours[0])

    assert can_access_chapter(learner, parcours[2]) is True
