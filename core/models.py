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
    Rôles : DG (accès total), Directeur Technique, Directeur Financier, Agent.
    """

    class Role(models.TextChoices):
        CHEF = 'chef', _("Directeur Général")
        DIRECTEUR_TECHNIQUE = 'directeur_technique', _("Directeur Technique")
        DIRECTEUR_FINANCIER = 'directeur_financier', _("Directeur Financier")
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
        max_length=25,
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
        """Vrai si DG (alias is_dg pour compatibilité)."""
        return self.role == self.Role.CHEF

    @property
    def is_dg(self) -> bool:
        """Vrai si Directeur Général."""
        return self.role == self.Role.CHEF

    @property
    def is_dt(self) -> bool:
        """Vrai si Directeur Technique."""
        return self.role == self.Role.DIRECTEUR_TECHNIQUE

    @property
    def is_df(self) -> bool:
        """Vrai si Directeur Financier."""
        return self.role == self.Role.DIRECTEUR_FINANCIER

    @property
    def is_agent(self) -> bool:
        """Vrai si Agent."""
        return self.role == self.Role.AGENT

    @property
    def is_directeur(self) -> bool:
        """Vrai si DT ou DF."""
        return self.role in (self.Role.DIRECTEUR_TECHNIQUE, self.Role.DIRECTEUR_FINANCIER)

    @property
    def role_display(self) -> str:
        """Libellé court du rôle pour la sidebar."""
        labels = {
            'chef': 'Directeur Général',
            'directeur_technique': 'Directeur Technique',
            'directeur_financier': 'Directeur Financier',
            'agent': 'Agent',
        }
        return labels.get(self.role, self.role)

    @property
    def role_display_badge(self) -> str:
        """Classe CSS DaisyUI selon le rôle."""
        if self.is_chef:
            return 'badge-primary'
        if self.is_directeur:
            return 'badge-warning'
        return 'badge-secondary'


class EmailConfig(models.Model):
    """
    Configuration SMTP stockée en base — singleton (pk=1 toujours).
    Priorité sur les settings du fichier .env dès qu'un enregistrement existe.
    """
    email_backend = models.CharField(
        max_length=150,
        default='django.core.mail.backends.smtp.EmailBackend',
        verbose_name="Backend email",
    )
    email_host = models.CharField(
        max_length=255,
        default='smtp.gmail.com',
        verbose_name="Serveur SMTP",
    )
    email_port = models.PositiveIntegerField(
        default=465,
        verbose_name="Port SMTP",
    )
    email_use_ssl = models.BooleanField(
        default=True,
        verbose_name="SSL (port 465)",
    )
    email_use_tls = models.BooleanField(
        default=False,
        verbose_name="TLS (port 587)",
    )
    email_host_user = models.EmailField(
        blank=True,
        verbose_name="Compte expéditeur (email)",
    )
    email_host_password = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Mot de passe / App Password",
    )
    default_from_email = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nom et adresse d'expédition",
        help_text='Exemple : Atlas Énergies <noreply@atlas-energies.ci>',
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        verbose_name = "Configuration email"
        verbose_name_plural = "Configuration email"

    def __str__(self):
        return f"Config email — {self.email_host}:{self.email_port}"

    def save(self, *args, **kwargs):
        self.pk = 1  # Singleton
        super().save(*args, **kwargs)
        self.apply_to_settings()

    def delete(self, *args, **kwargs):
        pass  # Empêche la suppression du singleton

    @classmethod
    def get_solo(cls):
        from django.conf import settings
        obj, _ = cls.objects.get_or_create(pk=1)
        # Si jamais configuré via l'interface (email_host_user vide),
        # on préremplie depuis les valeurs .env pour que le formulaire
        # affiche d'emblée ce qui est déjà en production.
        if not obj.email_host_user:
            obj.email_host = getattr(settings, 'EMAIL_HOST', obj.email_host)
            obj.email_port = getattr(settings, 'EMAIL_PORT', obj.email_port)
            obj.email_use_ssl = getattr(settings, 'EMAIL_USE_SSL', obj.email_use_ssl)
            obj.email_use_tls = getattr(settings, 'EMAIL_USE_TLS', obj.email_use_tls)
            obj.email_host_user = getattr(settings, 'EMAIL_HOST_USER', '')
            obj.email_host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
            obj.default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '')
            if obj.email_host_user:
                obj.save()
        return obj

    def apply_to_settings(self):
        """Surcharge les settings Django en mémoire avec les valeurs de la BD."""
        from django.conf import settings
        settings.EMAIL_BACKEND = self.email_backend
        settings.EMAIL_HOST = self.email_host
        settings.EMAIL_PORT = self.email_port
        settings.EMAIL_USE_SSL = self.email_use_ssl
        settings.EMAIL_USE_TLS = self.email_use_tls
        settings.EMAIL_HOST_USER = self.email_host_user
        settings.EMAIL_HOST_PASSWORD = self.email_host_password
        settings.DEFAULT_FROM_EMAIL = (
            self.default_from_email or self.email_host_user
        )
