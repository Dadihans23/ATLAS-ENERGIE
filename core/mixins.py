"""
Mixins de contrôle d'accès par rôle.
Utilisés dans toutes les CBV qui nécessitent une vérification de rôle.
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class ChefRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Réserve la vue au Directeur Général."""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_chef

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()


class DirecteurTechniqueRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Réserve la vue au Directeur Technique."""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_dt

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()


class DirecteurFinancierRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Réserve la vue au Directeur Financier."""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_df

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()


class DirecteurOuDGMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Réserve la vue aux directeurs (DT, DF) et au DG."""

    def test_func(self):
        u = self.request.user
        return u.is_authenticated and (u.is_chef or u.is_dt or u.is_df)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()


class AgentOrChefRequiredMixin(LoginRequiredMixin):
    """Autorise tout utilisateur authentifié."""
    pass
