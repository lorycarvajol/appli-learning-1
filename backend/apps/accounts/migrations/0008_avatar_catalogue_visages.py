"""
Bascule du catalogue d'avatars : formes abstraites → visages illustrés.

Les anciennes clés (`orbit-violet`, `prism-amber`, `mesh-lime`…) ne figurent
plus au catalogue. Le rendu client retombe déjà proprement sur les initiales
pour une clé inconnue, donc rien n'est cassé à l'écran — mais laisser ces
valeurs en base poserait deux problèmes :

- elles sont désormais **refusées en écriture** par
  `ProfileSerializer.validate_avatar_key` : un apprenant qui enregistrerait
  son profil sans toucher à son avatar verrait sa sauvegarde échouer sur un
  champ qu'il n'a pas modifié ;
- on ne saurait plus distinguer « n'a jamais choisi » de « avait choisi une
  forme qui n'existe plus ».

On les remet donc à la valeur « pas de choix », c'est-à-dire les initiales
colorées — l'état par défaut de tout compte.

Irréversible au sens strict : le retour arrière ne peut pas deviner quelle
forme chacun avait choisie. On l'assume plutôt que de simuler une réversibilité
mensongère.
"""

from django.db import migrations

from apps.accounts.avatars import avatar_choices


def purger_cles_obsoletes(apps, schema_editor):
    Profile = apps.get_model('accounts', 'Profile')
    Profile.objects.exclude(avatar_key='').exclude(
        avatar_key__in=avatar_choices()
    ).update(avatar_key='')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_remove_profile_avatar'),
    ]

    operations = [
        migrations.RunPython(
            purger_cles_obsoletes,
            migrations.RunPython.noop,
        ),
    ]
