"""
Mixins de contrôle d'accès par rôle.
Utilisés dans toutes les CBV qui nécessitent une vérification de rôle.
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class ChefRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Réserve la vue aux utilisateurs ayant le rôle Chef d'Agence."""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_chef

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()


class AgentOrChefRequiredMixin(LoginRequiredMixin):
    """Autorise tout utilisateur authentifié (Chef ou Agent)."""
    pass
