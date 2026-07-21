"""
Signals for automatic profile creation.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile whenever a new User is created."""
    if created:
        Profile.objects.get_or_create(user=instance)


# NOTE : il existait ici un second receveur `save_user_profile` qui appelait
# `instance.profile.save()` à chaque sauvegarde du User. Il a été supprimé —
# c'était une perte de données silencieuse.
#
# `instance.profile` renvoie l'objet chargé en mémoire. Si les points ont été
# crédités entre-temps par une autre instance (ce que fait `award_points`, qui
# relit le profil avec `select_for_update`), ce `save()` réécrivait l'ancien
# solde par-dessus. Un simple `user.save()` — déclenché par exemple par la
# mise à jour de `last_login` à chaque connexion — annulait alors les points
# gagnés dans la même requête.
#
# Le profil n'a pas besoin d'être sauvé quand le User change : ce sont deux
# tables distinctes, chacune écrite par son propre code.
