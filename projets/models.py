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
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class ActiveProjetManager(models.Manager):
    """Manager par défaut — exclut les projets soft-deleted."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Projet(models.Model):
    """
    Projet d'agence avec 5 lignes budgétaires exploitation + 17 lignes FG en XOF.
    Les budgets consommés sont mis à jour automatiquement via des signaux
    à chaque création / modification / suppression d'une dépense.
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

    # ── Budgets alloués – Frais Généraux (XOF) ───────────────────────────────
    budget_fg_loyers = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – Loyers (XOF)"))
    budget_fg_cie = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – CIE (XOF)"))
    budget_fg_sodeci = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – SODECI (XOF)"))
    budget_fg_dotation_carburant = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – Dotation carburant (XOF)"))
    budget_fg_frais_taxi = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – Frais taxi (XOF)"))
    budget_fg_fournitures_bureau = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – Fournitures bureau (XOF)"))
    budget_fg_produits_entretien = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – Produits entretien & droguerie (XOF)"))
    budget_fg_assurance_sante = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – Assurance santé (XOF)"))
    budget_fg_charges_personnel = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – Charges personnel (XOF)"))
    budget_fg_telephone_fixe = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – Téléphone fixe & internet (XOF)"))
    budget_fg_telephone_cellulaire = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – Téléphone cellulaire (XOF)"))
    budget_fg_entretien_vehicule = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – Entretien véhicule (XOF)"))
    budget_fg_impots = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – Impôts (XOF)"))
    budget_fg_bic = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – BIC (XOF)"))
    budget_fg_patente = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – Patente (XOF)"))
    budget_fg_cnps = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – CNPS (XOF)"))
    budget_fg_entretien_informatique = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_("FG – Entretien informatique & télécom (XOF)"))

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

    # ── Dépenses cumulées – Frais Généraux (mis à jour par signaux) ───────────
    depense_fg_loyers = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – Loyers (XOF)"))
    depense_fg_cie = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – CIE (XOF)"))
    depense_fg_sodeci = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – SODECI (XOF)"))
    depense_fg_dotation_carburant = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – Dotation carburant (XOF)"))
    depense_fg_frais_taxi = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – Frais taxi (XOF)"))
    depense_fg_fournitures_bureau = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – Fournitures bureau (XOF)"))
    depense_fg_produits_entretien = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – Produits entretien & droguerie (XOF)"))
    depense_fg_assurance_sante = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – Assurance santé (XOF)"))
    depense_fg_charges_personnel = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – Charges personnel (XOF)"))
    depense_fg_telephone_fixe = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – Téléphone fixe & internet (XOF)"))
    depense_fg_telephone_cellulaire = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – Téléphone cellulaire (XOF)"))
    depense_fg_entretien_vehicule = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – Entretien véhicule (XOF)"))
    depense_fg_impots = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – Impôts (XOF)"))
    depense_fg_bic = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – BIC (XOF)"))
    depense_fg_patente = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – Patente (XOF)"))
    depense_fg_cnps = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – CNPS (XOF)"))
    depense_fg_entretien_informatique = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False, verbose_name=_("Consommé FG – Entretien informatique & télécom (XOF)"))

    # ── Méta ──────────────────────────────────────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Projet actif"),
        db_index=True,
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name=_("Archivé (supprimé)"),
        db_index=True,
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Archivé le"),
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

    # ── Managers ──────────────────────────────────────────────────────────────
    objects = ActiveProjetManager()       # par défaut : exclut les archivés
    all_objects = models.Manager()        # accès complet (admin, audit)

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
        """Somme de toutes les lignes budgétaires allouées (exploitation + FG)."""
        return (
            self.budget_etude
            + self.budget_materiel_equipement
            + self.budget_logistique
            + self.budget_soustraitance
            + self.budget_frais_mission
            + self.total_budget_fg
        )

    @property
    def total_budget_exploitation(self) -> Decimal:
        """Somme des lignes budgétaires exploitation uniquement."""
        return (
            self.budget_etude
            + self.budget_materiel_equipement
            + self.budget_logistique
            + self.budget_soustraitance
            + self.budget_frais_mission
        )

    @property
    def total_budget_fg(self) -> Decimal:
        """Somme des lignes budgétaires frais généraux."""
        return (
            self.budget_fg_loyers + self.budget_fg_cie + self.budget_fg_sodeci
            + self.budget_fg_dotation_carburant + self.budget_fg_frais_taxi
            + self.budget_fg_fournitures_bureau + self.budget_fg_produits_entretien
            + self.budget_fg_assurance_sante + self.budget_fg_charges_personnel
            + self.budget_fg_telephone_fixe + self.budget_fg_telephone_cellulaire
            + self.budget_fg_entretien_vehicule + self.budget_fg_impots
            + self.budget_fg_bic + self.budget_fg_patente
            + self.budget_fg_cnps + self.budget_fg_entretien_informatique
        )

    @property
    def total_depense(self) -> Decimal:
        """Total consommé sur toutes les lignes (exploitation + FG)."""
        return self.total_depense_exploitation + self.total_depense_fg

    @property
    def total_depense_exploitation(self) -> Decimal:
        """Total consommé exploitation."""
        return (
            self.depense_etude
            + self.depense_materiel_equipement
            + self.depense_logistique
            + self.depense_soustraitance
            + self.depense_frais_mission
        )

    @property
    def total_depense_fg(self) -> Decimal:
        """Total consommé frais généraux."""
        return (
            self.depense_fg_loyers + self.depense_fg_cie + self.depense_fg_sodeci
            + self.depense_fg_dotation_carburant + self.depense_fg_frais_taxi
            + self.depense_fg_fournitures_bureau + self.depense_fg_produits_entretien
            + self.depense_fg_assurance_sante + self.depense_fg_charges_personnel
            + self.depense_fg_telephone_fixe + self.depense_fg_telephone_cellulaire
            + self.depense_fg_entretien_vehicule + self.depense_fg_impots
            + self.depense_fg_bic + self.depense_fg_patente
            + self.depense_fg_cnps + self.depense_fg_entretien_informatique
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
        """Vrai si au moins une ligne (exploitation ou FG) dépasse son budget."""
        exp = (
            self.depense_etude > self.budget_etude
            or self.depense_materiel_equipement > self.budget_materiel_equipement
            or self.depense_logistique > self.budget_logistique
            or self.depense_soustraitance > self.budget_soustraitance
            or self.depense_frais_mission > self.budget_frais_mission
        )
        fg = any(
            getattr(self, f'depense_fg_{k}') > getattr(self, f'budget_fg_{k}')
            for k in self.FG_DEPENSE_FIELD_MAP
        )
        return exp or fg

    # ── Mapping ligne → champ depense_* exploitation (utilisé par les signaux) ─
    DEPENSE_FIELD_MAP: dict[str, str] = {
        'etude': 'depense_etude',
        'materiel': 'depense_materiel_equipement',
        'logistique': 'depense_logistique',
        'soustraitance': 'depense_soustraitance',
        'frais_mission': 'depense_frais_mission',
    }

    # ── Mapping ligne → champ depense_fg_* (utilisé par les signaux FG) ────────
    FG_DEPENSE_FIELD_MAP: dict[str, str] = {
        'loyers': 'depense_fg_loyers',
        'cie': 'depense_fg_cie',
        'sodeci': 'depense_fg_sodeci',
        'dotation_carburant': 'depense_fg_dotation_carburant',
        'frais_taxi': 'depense_fg_frais_taxi',
        'fournitures_bureau': 'depense_fg_fournitures_bureau',
        'produits_entretien': 'depense_fg_produits_entretien',
        'assurance_sante': 'depense_fg_assurance_sante',
        'charges_personnel': 'depense_fg_charges_personnel',
        'telephone_fixe': 'depense_fg_telephone_fixe',
        'telephone_cellulaire': 'depense_fg_telephone_cellulaire',
        'entretien_vehicule': 'depense_fg_entretien_vehicule',
        'impots': 'depense_fg_impots',
        'bic': 'depense_fg_bic',
        'patente': 'depense_fg_patente',
        'cnps': 'depense_fg_cnps',
        'entretien_informatique': 'depense_fg_entretien_informatique',
    }

    def get_depense_field(self, ligne_budgetaire: str) -> str:
        """Retourne le nom du champ depense_* correspondant à la ligne exploitation."""
        return self.DEPENSE_FIELD_MAP[ligne_budgetaire]

    def get_fg_depense_field(self, ligne_budgetaire: str) -> str:
        """Retourne le nom du champ depense_fg_* correspondant à la ligne FG."""
        return self.FG_DEPENSE_FIELD_MAP[ligne_budgetaire]
