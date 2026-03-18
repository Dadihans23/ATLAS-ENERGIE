"""
Modèle utilisateur personnalisé – Atlas Énergies.

Architecture :
- Email comme identifiant principal (pas de username)
- Rôle intégré (CHEF / AGENT) + groupes Django pour les permissions
- HistoricalRecords pour audit complet
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from simple_history.models import HistoricalRecords

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Utilisateur Atlas Énergies.
    Deux rôles : Chef d'Agence (accès total) et Agent (saisie dépenses uniquement).
    """

    class Role(models.TextChoices):
        CHEF = 'chef', _("Chef d'Agence")
        AGENT = 'agent', _("Agent")

    # ── Identité ──────────────────────────────────────────────────────────────
    email = models.EmailField(
        unique=True,
        verbose_name=_("Adresse email"),
        help_text=_("Utilisé comme identifiant de connexion."),
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name=_("Prénom"),
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name=_("Nom de famille"),
    )

    # ── Rôle ──────────────────────────────────────────────────────────────────
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.AGENT,
        verbose_name=_("Rôle"),
        db_index=True,
    )

    # ── Statut Django ─────────────────────────────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Compte actif"),
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("Accès à l'administration"),
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Date d'inscription"),
    )

    # ── Audit ─────────────────────────────────────────────────────────────────
    history = HistoricalRecords(verbose_name=_("Historique"))

    # ── Configuration ─────────────────────────────────────────────────────────
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")
        ordering = ['last_name', 'first_name']

    # ── Représentation ────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f"{self.get_full_name()} <{self.email}>"

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        return self.first_name

    # ── Propriétés de rôle ────────────────────────────────────────────────────
    @property
    def is_chef(self) -> bool:
        """Vrai si l'utilisateur est Chef d'Agence."""
        return self.role == self.Role.CHEF

    @property
    def is_agent(self) -> bool:
        """Vrai si l'utilisateur est Agent."""
        return self.role == self.Role.AGENT

    @property
    def role_display_badge(self) -> str:
        """Classe CSS DaisyUI selon le rôle (pour les templates)."""
        return 'badge-primary' if self.is_chef else 'badge-secondary'
