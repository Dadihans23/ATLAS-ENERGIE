"""
Modèles de dépenses – Atlas Énergies.

Deux types :
1. DepenseExploitation  → déduit du budget du Projet (signal post_save/post_delete)
2. DepenseFraisGeneraux → dépenses générales, ne touche PAS au budget projet

Architecture clé :
- montant_xof stocké au moment de la saisie (taux figé) → cohérence historique
- numero_saisie auto-généré dans save() avec verrou SELECT FOR UPDATE
- piece_jointe validée (extension + taille) + path versionné YYYY/MM/
- HistoricalRecords sur les deux modèles pour audit complet
"""
import os
import uuid
from decimal import Decimal
from pathlib import Path as FilePath

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from projets.models import Projet
from .validators import validate_file_extension, validate_file_size, validate_montant_positif


# ─── Choix partagés ───────────────────────────────────────────────────────────

class Devise(models.TextChoices):
    XOF = 'XOF', 'XOF (Franc CFA)'
    EUR = 'EUR', 'EUR (Euro)'
    USD = 'USD', 'USD (Dollar US)'


# ─── Chemins d'upload ─────────────────────────────────────────────────────────

def exploitation_upload_path(instance, filename):
    """
    Stocke les PJ sous media/depenses/exploitation/YYYY/MM/
    Nom de fichier aléatoire (uuid4) pour éviter collisions et path disclosure.
    """
    ext = FilePath(filename).suffix.lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    now = instance.date_saisie or timezone.now().date()
    return f"depenses/exploitation/{now.year}/{now.month:02d}/{safe_name}"


def frais_generaux_upload_path(instance, filename):
    """
    Stocke les PJ sous media/depenses/frais_generaux/YYYY/MM/
    Nom de fichier aléatoire (uuid4) pour éviter collisions et path disclosure.
    """
    ext = FilePath(filename).suffix.lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    now = instance.date_saisie or timezone.now().date()
    return f"depenses/frais_generaux/{now.year}/{now.month:02d}/{safe_name}"


# ─── Génération numéro de saisie (thread-safe) ────────────────────────────────

def _next_numero(prefix: str, model_class, year: int) -> str:
    """
    Génère le prochain numéro de saisie de la forme PREFIX-YYYY-XXXXX.
    Doit être appelé à l'intérieur d'un transaction.atomic() + select_for_update().
    """
    last = (
        model_class.objects
        .select_for_update()
        .filter(numero_saisie__startswith=f"{prefix}-{year}-")
        .order_by('numero_saisie')
        .last()
    )
    if last:
        last_seq = int(last.numero_saisie.split('-')[-1])
        seq = last_seq + 1
    else:
        seq = 1
    return f"{prefix}-{year}-{seq:05d}"


# ─── Manager soft-delete ─────────────────────────────────────────────────────

class ActiveDepenseManager(models.Manager):
    """Manager par défaut — exclut les dépenses soft-deleted."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


# ─── Statut workflow ─────────────────────────────────────────────────────────

class StatutDepense(models.TextChoices):
    SOUMIS        = 'soumis',        _("Soumis")
    APPROUVE_N1   = 'approuve_n1',   _("Approuvé (Directeur)")
    APPROUVE_DG   = 'approuve_dg',   _("Approuvé (DG)")
    REJETE        = 'rejete',        _("Rejeté")
    DECAISSE      = 'decaisse',      _("Décaissé")


# ─── Modèle abstrait commun ───────────────────────────────────────────────────

class DepenseBase(models.Model):
    """
    Champs communs aux deux types de dépenses.
    Classe abstraite – pas de table en base.
    """

    # ── Champs communs ────────────────────────────────────────────────────────
    date_saisie = models.DateField(
        default=timezone.now,
        verbose_name=_("Date de saisie"),
        db_index=True,
    )
    libelle = models.TextField(
        verbose_name=_("Libellé"),
    )
    devise = models.CharField(
        max_length=3,
        choices=Devise.choices,
        default=Devise.XOF,
        verbose_name=_("Devise"),
    )
    montant = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[validate_montant_positif],
        verbose_name=_("Montant"),
    )
    montant_xof = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        verbose_name=_("Montant converti XOF"),
        help_text=_("Calculé automatiquement selon le taux au moment de la saisie."),
    )
    taux_change_utilise = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('1.0000'),
        editable=False,
        verbose_name=_("Taux de change utilisé"),
    )
    fournisseur = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Fournisseur"),
    )
    numero_piece = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Numéro de pièce"),
    )
    commentaire = models.TextField(
        blank=True,
        verbose_name=_("Commentaire"),
    )
    numero_saisie = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        verbose_name=_("Numéro de saisie"),
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_("Saisi par"),
    )
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Créé le"),
    )
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Modifié le"),
    )

    # ── Workflow validation ───────────────────────────────────────────────────
    statut = models.CharField(
        max_length=15,
        choices=StatutDepense.choices,
        default=StatutDepense.SOUMIS,
        verbose_name=_("Statut"),
        db_index=True,
    )
    valide_par_n1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='+',
        verbose_name=_("Validé par (Directeur)"),
    )
    date_validation_n1 = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("Date validation directeur"),
    )
    motif_rejet_n1 = models.TextField(
        blank=True,
        verbose_name=_("Motif rejet directeur"),
    )
    valide_par_dg = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='+',
        verbose_name=_("Validé par (DG)"),
    )
    date_validation_dg = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("Date validation DG"),
    )
    motif_rejet_dg = models.TextField(
        blank=True,
        verbose_name=_("Motif rejet DG"),
    )
    decaisse_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='+',
        verbose_name=_("Décaissé par"),
    )
    date_decaissement = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("Date de décaissement"),
    )

    # ── Soft delete ───────────────────────────────────────────────────────────
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

    class Meta:
        abstract = True

    def _calculer_montant_xof(self) -> tuple[Decimal, Decimal]:
        """
        Convertit self.montant en XOF selon self.devise.
        Retourne (montant_xof, taux_utilise).
        Le taux EUR/XOF est fixe (parité officielle CFA).
        """
        if self.devise == Devise.XOF:
            return self.montant, Decimal('1.0000')
        elif self.devise == Devise.EUR:
            taux = getattr(settings, 'TAUX_EUR_XOF', Decimal('655.957'))
            taux = Decimal(str(taux))
            return (self.montant * taux).quantize(Decimal('0.01')), taux
        elif self.devise == Devise.USD:
            taux = getattr(settings, 'TAUX_USD_XOF', Decimal('605.00'))
            taux = Decimal(str(taux))
            return (self.montant * taux).quantize(Decimal('0.01')), taux
        return self.montant, Decimal('1.0000')


# ─── DepenseExploitation ──────────────────────────────────────────────────────

class DepenseExploitation(DepenseBase):
    """
    Dépense liée à un Projet – déduit du budget correspondant.
    Numéro de saisie : EXP-YYYY-XXXXX
    """

    class LigneBudgetaire(models.TextChoices):
        ETUDE = 'etude', _("Étude")
        MATERIEL = 'materiel', _("Matériel et équipement")
        LOGISTIQUE = 'logistique', _("Logistique")
        SOUSTRAITANCE = 'soustraitance', _("Sous-traitance")
        FRAIS_MISSION = 'frais_mission', _("Frais de mission")

    class NatureDepense(models.TextChoices):
        PROFORMAT = 'proformat', _("Proformat")
        BON_COMMANDE = 'bon_commande', _("Bon de commande")
        DEMANDE_ACHAT = 'demande_achat', _("Demande d'achat")
        FACTURE = 'facture', _("Facture")

    # ── Champs spécifiques ────────────────────────────────────────────────────
    centre_budgetaire = models.ForeignKey(
        Projet,
        on_delete=models.PROTECT,
        related_name='depenses_exploitation',
        verbose_name=_("Centre budgétaire (Projet)"),
        db_index=True,
    )
    ligne_budgetaire = models.CharField(
        max_length=20,
        choices=LigneBudgetaire.choices,
        verbose_name=_("Ligne budgétaire"),
        db_index=True,
    )
    nature_depense = models.CharField(
        max_length=20,
        choices=NatureDepense.choices,
        verbose_name=_("Nature de la dépense"),
    )
    piece_jointe = models.FileField(
        upload_to=exploitation_upload_path,
        blank=True,
        null=True,
        validators=[validate_file_extension, validate_file_size],
        verbose_name=_("Pièce jointe"),
    )

    # ── Managers ──────────────────────────────────────────────────────────────
    objects = ActiveDepenseManager()
    all_objects = models.Manager()

    # ── Audit ─────────────────────────────────────────────────────────────────
    history = HistoricalRecords(verbose_name=_("Historique"))

    class Meta:
        verbose_name = _("Dépense d'exploitation")
        verbose_name_plural = _("Dépenses d'exploitation")
        ordering = ['-date_saisie', '-date_creation']
        indexes = [
            models.Index(fields=['centre_budgetaire', 'ligne_budgetaire']),
            models.Index(fields=['date_saisie']),
        ]

    def __str__(self) -> str:
        return f"{self.numero_saisie} – {self.libelle[:60]}"

    def save(self, *args, **kwargs):
        # 1. Convertir le montant en XOF
        self.montant_xof, self.taux_change_utilise = self._calculer_montant_xof()

        # 2. Générer le numéro de saisie (seulement à la création)
        if not self.numero_saisie:
            with transaction.atomic():
                year = self.date_saisie.year if isinstance(self.date_saisie, type(timezone.now().date())) else timezone.now().year
                # On s'assure de récupérer l'année correctement
                try:
                    year = self.date_saisie.year
                except AttributeError:
                    year = timezone.now().year
                self.numero_saisie = _next_numero('EXP', DepenseExploitation, year)
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def piece_jointe_filename(self) -> str:
        """Nom de fichier uniquement (sans le chemin complet)."""
        if self.piece_jointe:
            return os.path.basename(self.piece_jointe.name)
        return ''


# ─── DepenseFraisGeneraux ─────────────────────────────────────────────────────

class DepenseFraisGeneraux(DepenseBase):
    """
    Dépense de fonctionnement général – NE touche PAS au budget projet.
    Numéro de saisie : FG-YYYY-XXXXX
    """

    class LigneBudgetaire(models.TextChoices):
        LOYERS = 'loyers', _("Loyers")
        CIE = 'cie', _("CIE")
        SODECI = 'sodeci', _("SODECI")
        DOTATION_CARBURANT = 'dotation_carburant', _("Dotation carburant")
        FRAIS_TAXI = 'frais_taxi', _("Frais taxi")
        FOURNITURES_BUREAU = 'fournitures_bureau', _("Fournitures bureau")
        PRODUITS_ENTRETIEN = 'produits_entretien', _("Produits entretien & droguerie")
        ASSURANCE_SANTE = 'assurance_sante', _("Assurance santé")
        CHARGES_PERSONNEL = 'charges_personnel', _("Charges personnel")
        TELEPHONE_FIXE = 'telephone_fixe', _("Téléphone fixe & internet")
        TELEPHONE_CELLULAIRE = 'telephone_cellulaire', _("Téléphone cellulaire")
        ENTRETIEN_VEHICULE = 'entretien_vehicule', _("Entretien véhicule")
        IMPOTS = 'impots', _("Impôts")
        BIC = 'bic', _("BIC")
        PATENTE = 'patente', _("Patente")
        CNPS = 'cnps', _("CNPS")
        ENTRETIEN_INFORMATIQUE = 'entretien_informatique', _("Entretien informatique & télécom")

    class NatureDepense(models.TextChoices):
        DEMANDE_ACHAT = 'demande_achat', _("Demande d'achat")
        BON_COMMANDE = 'bon_commande', _("Bon de commande")
        DEMANDE_PAIEMENT = 'demande_paiement', _("Demande de paiement")
        DEMANDE_TRAVAIL = 'demande_travail', _("Demande de travail")
        DEMANDE_ABSENCE = 'demande_absence', _("Demande d'absence")
        FACTURE = 'facture', _("Facture")
        FRAIS_MISSION = 'frais_mission', _("Frais de mission")
        RESERVATION = 'reservation', _("Réservation")

    # ── Champs spécifiques ────────────────────────────────────────────────────
    centre_budgetaire = models.ForeignKey(
        Projet,
        on_delete=models.PROTECT,
        related_name='depenses_frais_generaux',
        verbose_name=_("Projet"),
        db_index=True,
    )
    ligne_budgetaire = models.CharField(
        max_length=30,
        choices=LigneBudgetaire.choices,
        verbose_name=_("Ligne budgétaire"),
        db_index=True,
    )
    nature_depense = models.CharField(
        max_length=20,
        choices=NatureDepense.choices,
        verbose_name=_("Nature de la dépense"),
    )
    piece_jointe = models.FileField(
        upload_to=frais_generaux_upload_path,
        blank=True,
        null=True,
        validators=[validate_file_extension, validate_file_size],
        verbose_name=_("Pièce jointe"),
    )

    # ── Managers ──────────────────────────────────────────────────────────────
    objects = ActiveDepenseManager()
    all_objects = models.Manager()

    # ── Audit ─────────────────────────────────────────────────────────────────
    history = HistoricalRecords(verbose_name=_("Historique"))

    class Meta:
        verbose_name = _("Dépense de frais généraux")
        verbose_name_plural = _("Dépenses de frais généraux")
        ordering = ['-date_saisie', '-date_creation']
        indexes = [
            models.Index(fields=['ligne_budgetaire', 'date_saisie']),
        ]

    def __str__(self) -> str:
        return f"{self.numero_saisie} – {self.libelle[:60]}"

    def save(self, *args, **kwargs):
        # 1. Convertir en XOF
        self.montant_xof, self.taux_change_utilise = self._calculer_montant_xof()

        # 2. Générer le numéro de saisie (création uniquement)
        if not self.numero_saisie:
            with transaction.atomic():
                try:
                    year = self.date_saisie.year
                except AttributeError:
                    year = timezone.now().year
                self.numero_saisie = _next_numero('FG', DepenseFraisGeneraux, year)
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def piece_jointe_filename(self) -> str:
        if self.piece_jointe:
            return os.path.basename(self.piece_jointe.name)
        return ''
