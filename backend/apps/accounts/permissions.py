"""Permissions partagées, basées sur le rôle."""
from rest_framework.permissions import IsAuthenticated

from .models import User


class IsTrainerOrAdmin(IsAuthenticated):
    """Réservé aux formateurs et aux administrateurs."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in (User.Role.TRAINER, User.Role.ADMIN)


class IsAdmin(IsAuthenticated):
    """Réservé aux administrateurs.

    Sert notamment à cloisonner l'émission d'invitations de rôle TRAINER :
    un formateur ne doit pas pouvoir en recruter d'autres.
    """

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role == User.Role.ADMIN
