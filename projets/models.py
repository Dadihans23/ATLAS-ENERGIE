"""
Modèle Projet – Atlas Énergies.

Architecture :
- 5 lignes budgétaires correspondant exactement aux choix de dépenses
- Champs depense_* mis à jour atomiquement par les signaux de depenses/
- Propriétés calculées (total, restants, taux) jamais stockées → cohérence garantie
- HistoricalRecords pour audit complet (django-simple-history)
"""
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class Projet(models.Model):
    """
    Projet d'agence avec 5 lignes budgétaires en XOF.
    Le budget consommé est mis à jour automatiquement via des signaux
    à chaque création / modification / suppression d'une DepenseExploitation.
    """

    # ── Identification ────────────────────────────────────────────────────────
    nom = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Nom du projet"),
    )
    designation = models.TextField(
        verbose_name=_("Désignation / Description"),
        blank=True,
    )

    # ── Budgets alloués (XOF) ─────────────────────────────────────────────────
    budget_etude = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_("Budget Étude (XOF)"),
    )
    budget_materiel_equipement = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_("Budget Matériel & Équipement (XOF)"),
    )
    budget_logistique = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_("Budget Logistique (XOF)"),
    )
    budget_soustraitance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_("Budget Sous-traitance (XOF)"),
    )
    budget_frais_mission = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_("Budget Frais de Mission (XOF)"),
    )

    # ── Dépenses cumulées par ligne (mis à jour par signaux – ne pas modifier manuellement) ──
    depense_etude = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Consommé Étude (XOF)"),
        editable=False,
    )
    depense_materiel_equipement = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Consommé Matériel & Équipement (XOF)"),
        editable=False,
    )
    depense_logistique = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Consommé Logistique (XOF)"),
        editable=False,
    )
    depense_soustraitance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Consommé Sous-traitance (XOF)"),
        editable=False,
    )
    depense_frais_mission = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Consommé Frais de Mission (XOF)"),
        editable=False,
    )

    # ── Méta ──────────────────────────────────────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Projet actif"),
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='projets_crees',
        verbose_name=_("Créé par"),
    )
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date de création"),
    )
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Dernière modification"),
    )

    # ── Audit ─────────────────────────────────────────────────────────────────
    history = HistoricalRecords(verbose_name=_("Historique"))

    class Meta:
        verbose_name = _("Projet")
        verbose_name_plural = _("Projets")
        ordering = ['-date_creation']

    def __str__(self) -> str:
        return self.nom

    # ── Propriétés calculées ──────────────────────────────────────────────────

    @property
    def total_budget(self) -> Decimal:
        """Somme de toutes les lignes budgétaires allouées."""
        return (
            self.budget_etude
            + self.budget_materiel_equipement
            + self.budget_logistique
            + self.budget_soustraitance
            + self.budget_frais_mission
        )

    @property
    def total_depense(self) -> Decimal:
        """Total consommé sur toutes les lignes."""
        return (
            self.depense_etude
            + self.depense_materiel_equipement
            + self.depense_logistique
            + self.depense_soustraitance
            + self.depense_frais_mission
        )

    @property
    def budget_restant_global(self) -> Decimal:
        return self.total_budget - self.total_depense

    @property
    def restant_etude(self) -> Decimal:
        return self.budget_etude - self.depense_etude

    @property
    def restant_materiel_equipement(self) -> Decimal:
        return self.budget_materiel_equipement - self.depense_materiel_equipement

    @property
    def restant_logistique(self) -> Decimal:
        return self.budget_logistique - self.depense_logistique

    @property
    def restant_soustraitance(self) -> Decimal:
        return self.budget_soustraitance - self.depense_soustraitance

    @property
    def restant_frais_mission(self) -> Decimal:
        return self.budget_frais_mission - self.depense_frais_mission

    @property
    def taux_consommation(self) -> Decimal:
        """Pourcentage du budget global consommé (0-100+)."""
        if not self.total_budget:
            return Decimal('0.00')
        return (self.total_depense / self.total_budget * 100).quantize(Decimal('0.01'))

    @property
    def est_en_depassement(self) -> bool:
        """Vrai si au moins une ligne dépasse son budget."""
        return (
            self.depense_etude > self.budget_etude
            or self.depense_materiel_equipement > self.budget_materiel_equipement
            or self.depense_logistique > self.budget_logistique
            or self.depense_soustraitance > self.budget_soustraitance
            or self.depense_frais_mission > self.budget_frais_mission
        )

    # ── Mapping ligne → champ depense_* (utilisé par les signaux) ─────────────
    DEPENSE_FIELD_MAP: dict[str, str] = {
        'etude': 'depense_etude',
        'materiel': 'depense_materiel_equipement',
        'logistique': 'depense_logistique',
        'soustraitance': 'depense_soustraitance',
        'frais_mission': 'depense_frais_mission',
    }

    def get_depense_field(self, ligne_budgetaire: str) -> str:
        """Retourne le nom du champ depense_* correspondant à la ligne."""
        return self.DEPENSE_FIELD_MAP[ligne_budgetaire]
