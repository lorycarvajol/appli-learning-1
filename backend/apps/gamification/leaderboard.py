"""
Classement des apprenants.

Le grand livre de points contenait déjà tout ce qu'il faut : ce module ne
calcule rien de nouveau, il **ordonne** des soldes déjà garantis exacts par
``services.award_points`` (cf. l'invariant « le solde égale la somme du grand
livre »). Aucune écriture, aucun effet de bord.

Quatre décisions, toutes défendues par un test :

1. **Aucune donnée identifiante ne sort.** Pas d'email, pas de nom complet :
   le nom affiché est « Prénom N. », y compris pour soi-même. Un classement
   est la seule page où un apprenant voit les *autres* — c'est donc la seule
   qui puisse transformer une plateforme scolaire en annuaire.

2. **Le retrait est possible** (``Profile.show_in_leaderboard``). Se comparer
   motive les uns et décourage les autres ; on ne peut pas l'imposer. Un
   compte retiré garde ses points et ses badges, il ne figure simplement plus
   dans la liste — et n'y voit plus son propre rang, sinon le retrait serait
   cosmétique.

3. **Qui n'a aucun point n'est pas classé.** Un compte fraîchement créé
   n'arrive pas 57ᵉ ex æquo avec quarante autres : il n'est pas encore entré
   dans la course, et on le lui dit ainsi.

4. **Les ex æquo partagent leur rang** (1, 2, 2, 4 — pas 1, 2, 3, 4). Deux
   apprenants au même solde ont fait le même chemin ; les départager sur la
   date d'inscription afficherait une hiérarchie qui n'existe pas.

Le rang personnel est renvoyé **même hors du top** : un classement qui ne
montre que ses vingt premiers ne dit rien au vingt-et-unième, et c'est
précisément à lui qu'il devrait parler.
"""
from django.db.models import Count

from apps.accounts.models import Profile, User

#: Longueur du tableau renvoyée par défaut, et plafond dur. Le plafond n'est
#: pas défensif au sens sécurité — il borne le coût d'une requête que
#: n'importe quel apprenant peut déclencher en boucle.
DEFAULT_LIMIT = 20
MAX_LIMIT = 100

SCOPE_GLOBAL = 'global'
SCOPE_COHORT = 'cohort'
SCOPES = (SCOPE_GLOBAL, SCOPE_COHORT)


def participants():
    """Profils qui figurent au classement.

    Le filtre vit ici et **nulle part ailleurs** : le tableau, le rang
    personnel et le total sont tous construits sur ce même queryset. Une règle
    ajoutée d'un seul côté produirait un rang incohérent avec la liste.

    - ``is_active`` : un compte désactivé n'est plus sur la plateforme ;
    - ``LEARNER`` : un formateur qui parcourt son propre cours trusterait la
      tête du classement sans jamais avoir été l'élève de personne ;
    - ``anonymized_at`` : un compte effacé au sens RGPD ne désigne plus
      personne, l'afficher n'aurait pas de sens (et son nom est déjà vide) ;
    - ``show_in_leaderboard`` : le retrait volontaire ;
    - ``total_points > 0`` : voir le point 3 de l'en-tête de module.
    """
    return Profile.objects.filter(
        user__is_active=True,
        user__role=User.Role.LEARNER,
        anonymized_at__isnull=True,
        show_in_leaderboard=True,
        total_points__gt=0,
    )


def display_name(user):
    """Nom public : « Prénom N. ».

    Jamais l'email, y compris en repli — c'est un identifiant de connexion,
    et souvent « prenom.nom@etablissement.fr ». Un compte sans identité
    renseignée est simplement « Apprenant ».
    """
    first = (user.first_name or '').strip()
    last = (user.last_name or '').strip()

    if first and last:
        return f"{first} {last[0].upper()}."
    return first or last or 'Apprenant'


def _ranked_rows(queryset, limit, me_id):
    """Ordonne, annote et numérote — en attribuant le même rang aux ex æquo."""
    rows = (
        queryset
        .select_related('user')
        # `distinct=True` : sans lui, une seconde jointure ajoutée plus tard à
        # ce queryset multiplierait le comptage des badges.
        .annotate(badges_count=Count('user__badges', distinct=True))
        # Le second critère ne départage rien à l'affichage (les ex æquo
        # gardent le même rang) : il rend seulement l'ordre stable d'une
        # requête à l'autre, sans quoi deux chargements pourraient permuter
        # deux lignes au même solde.
        .order_by('-total_points', 'user__date_joined')[:limit]
    )

    payload = []
    previous_points = None
    previous_rank = 0

    for index, profile in enumerate(rows, start=1):
        if profile.total_points == previous_points:
            rank = previous_rank
        else:
            rank = index
        previous_points, previous_rank = profile.total_points, rank

        payload.append({
            'rank': rank,
            'display_name': display_name(profile.user),
            'avatar_key': profile.avatar_key,
            'points': profile.total_points,
            'level': profile.level,
            'badges_count': profile.badges_count,
            'is_me': profile.user_id == me_id,
        })

    return payload


def build_leaderboard(user, scope=SCOPE_GLOBAL, limit=DEFAULT_LIMIT):
    """Construit la charge utile du classement pour ``user``.

    Coût : **cinq requêtes, quel que soit le nombre d'apprenants** — le
    chargement du profil, le tableau, ma ligne, mon rang et le total. Un test
    le vérifie à deux volumes différents plutôt que par un plafond chiffré :
    c'est la page que toute une promo ouvre en même temps.
    """
    scope = scope if scope in SCOPES else SCOPE_GLOBAL
    limit = max(1, min(int(limit or DEFAULT_LIMIT), MAX_LIMIT))

    profile = getattr(user, 'profile', None)
    cohort_id = profile.cohort_id if profile else None

    if scope == SCOPE_COHORT and not cohort_id:
        # Un apprenant autonome n'a pas de classe : plutôt qu'un tableau vide
        # (qu'il lirait comme une panne), on dit pourquoi il n'y a rien.
        return {
            'scope': SCOPE_COHORT,
            'available': False,
            'reason': "Vous n'êtes rattaché à aucune classe.",
            'entries': [],
            'total_participants': 0,
            'me': None,
        }

    queryset = participants()
    if scope == SCOPE_COHORT:
        queryset = queryset.filter(cohort_id=cohort_id)

    me = None
    if profile is not None:
        my_row = (
            queryset
            .filter(pk=profile.pk)
            .select_related('user')
            .annotate(badges_count=Count('user__badges', distinct=True))
            .first()
        )
        if my_row is not None:
            me = {
                # Rang « de compétition » : le nombre d'apprenants strictement
                # devant, plus un. Cohérent par construction avec les ex æquo
                # du tableau, sans avoir à parcourir tout le classement.
                'rank': queryset.filter(
                    total_points__gt=my_row.total_points
                ).count() + 1,
                'display_name': display_name(my_row.user),
                'avatar_key': my_row.avatar_key,
                'points': my_row.total_points,
                'level': my_row.level,
                'badges_count': my_row.badges_count,
                'is_me': True,
            }

    return {
        'scope': scope,
        'available': True,
        'entries': _ranked_rows(queryset, limit, getattr(user, 'id', None)),
        'total_participants': queryset.count(),
        # `None` couvre deux situations distinctes, et le client les distingue
        # grâce à `participating` : ne pas avoir encore marqué de point, ou
        # s'être retiré du classement.
        'me': me,
        'participating': me is not None,
    }
