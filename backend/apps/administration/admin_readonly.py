"""
Outils pour cantonner l'admin Django à ce que l'espace React ne sait pas faire.

### Le partage des rôles

L'admin Django garde le **CRUD de contenu** (chapitres, leçons, exercices,
quiz, projets, catalogue de badges) : il le fait mieux et gratuitement, avec
recherche, filtres, inlines et historique. L'espace React garde le **pilotage**
(cycle de vie des comptes, affectation des formateurs, journal d'audit).

### Pourquoi ce n'est pas qu'une question de rangement

Tout ce que React pilote transite par `apps/administration/services.py`, qui
applique des garde-fous et **écrit le journal d'audit**. L'admin Django écrit
directement en base : un rôle changé depuis `/admin/` n'apparaissait dans aucun
journal, échappait à la règle du « dernier administrateur actif » et ne
révoquait aucune session.

Laisser les deux chemins ouverts revenait donc à laisser une porte dérobée à
côté de la porte qu'on venait de blinder. D'où le principe : **là où React est
l'autorité, l'admin Django n'est plus qu'un observatoire.**

Les données dérivées (progression, activité, grand livre de points) sont
verrouillées pour une raison distincte mais voisine : `Profile.total_points`
doit toujours égaler la somme des `PointTransaction`. Un ajustement à la main
décrochait le solde sans laisser de trace, et seul `recompute_profile_points`
pouvait ensuite expliquer l'écart.
"""
from django.contrib import admin


class ReadOnlyAdmin(admin.ModelAdmin):
    """Consultable et filtrable, mais jamais modifiable.

    On préfère la lecture seule au retrait pur et simple : répondre à
    « pourquoi cet apprenant a-t-il 340 points ? » demande de pouvoir fouiller
    la table. C'est le pouvoir d'inspection qu'on garde, pas celui d'écrire.
    """

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        """Tout est en lecture seule, y compris les champs non déclarés.

        Énumérer les champs à la main serait une dette : un champ ajouté au
        modèle plus tard redeviendrait éditable en silence.
        """
        return [field.name for field in self.model._meta.fields]
