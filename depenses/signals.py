"""
Signaux de dépenses – mise à jour atomique du budget Projet.

Stratégie :
- pre_save  → mémorise l'ancienne valeur (si modification)
- post_save → applique la différence sur le champ depense_* du Projet
- post_delete → restitue le montant au budget

Utilisation de F() expressions + update() pour éviter les race conditions.
Jamais de instance.save() sur Projet ici → pas d'historique parasite.

SÉCURITÉ (CRITICAL-03) :
- Les opérations multi-UPDATE sont enveloppées dans transaction.atomic()
- select_for_update() verrouille la ligne Projet pendant la transaction
"""
from django.db import transaction
from django.db.models import F
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from projets.models import Projet
from .models import DepenseExploitation, DepenseFraisGeneraux


# ─── Mémorisation de l'ancienne valeur avant modification ─────────────────────

@receiver(pre_save, sender=DepenseExploitation)
def memoriser_ancienne_depense(sender, instance: DepenseExploitation, **kwargs):
    """
    Avant la sauvegarde d'une dépense existante, charge l'ancienne instance
    pour pouvoir annuler son impact budgétaire.
    """
    if instance.pk:
        try:
            instance._ancienne_depense = DepenseExploitation.objects.get(pk=instance.pk)
        except DepenseExploitation.DoesNotExist:
            instance._ancienne_depense = None
    else:
        instance._ancienne_depense = None


# ─── Mise à jour du budget après sauvegarde ───────────────────────────────────

@receiver(post_save, sender=DepenseExploitation)
def mettre_a_jour_budget(sender, instance: DepenseExploitation, created: bool, **kwargs):
    """
    - Création : ajoute montant_xof au champ depense_* du Projet.
    - Modification : annule l'ancienne valeur, applique la nouvelle.

    Les deux opérations sont atomiques (transaction.atomic + select_for_update)
    pour éviter toute corruption budget en cas de crash ou concurrence.
    """
    ancienne = getattr(instance, '_ancienne_depense', None)

    with transaction.atomic():
        if not created and ancienne:
            # Annuler l'impact de l'ancienne dépense
            ancien_field = Projet.DEPENSE_FIELD_MAP.get(ancienne.ligne_budgetaire)
            if ancien_field:
                Projet.objects.select_for_update().filter(
                    pk=ancienne.centre_budgetaire_id
                ).update(**{ancien_field: F(ancien_field) - ancienne.montant_xof})

        # Appliquer la nouvelle dépense
        nouveau_field = Projet.DEPENSE_FIELD_MAP.get(instance.ligne_budgetaire)
        if nouveau_field:
            Projet.objects.select_for_update().filter(
                pk=instance.centre_budgetaire_id
            ).update(**{nouveau_field: F(nouveau_field) + instance.montant_xof})


# ─── Restitution du budget à la suppression ───────────────────────────────────

@receiver(post_delete, sender=DepenseExploitation)
def restituer_budget(sender, instance: DepenseExploitation, **kwargs):
    """
    À la suppression, restitue le montant_xof au champ depense_* du Projet.
    """
    field = Projet.DEPENSE_FIELD_MAP.get(instance.ligne_budgetaire)
    if field:
        with transaction.atomic():
            Projet.objects.select_for_update().filter(
                pk=instance.centre_budgetaire_id
            ).update(**{field: F(field) - instance.montant_xof})


# ═══════════════════════════════════════════════════════════════════════════════
# Signaux DepenseFraisGeneraux → mise à jour depense_fg_* sur Projet
# ═══════════════════════════════════════════════════════════════════════════════

@receiver(pre_save, sender=DepenseFraisGeneraux)
def memoriser_ancienne_depense_fg(sender, instance: DepenseFraisGeneraux, **kwargs):
    """Avant modification d'un FG existant, mémorise l'ancienne valeur."""
    if instance.pk:
        try:
            instance._ancienne_depense = DepenseFraisGeneraux.objects.get(pk=instance.pk)
        except DepenseFraisGeneraux.DoesNotExist:
            instance._ancienne_depense = None
    else:
        instance._ancienne_depense = None


@receiver(post_save, sender=DepenseFraisGeneraux)
def mettre_a_jour_budget_fg(sender, instance: DepenseFraisGeneraux, created: bool, **kwargs):
    """
    - Création : ajoute montant_xof au champ depense_fg_* du Projet.
    - Modification : annule l'ancienne valeur, applique la nouvelle.
    """
    ancienne = getattr(instance, '_ancienne_depense', None)

    with transaction.atomic():
        if not created and ancienne:
            ancien_field = Projet.FG_DEPENSE_FIELD_MAP.get(ancienne.ligne_budgetaire)
            if ancien_field:
                Projet.objects.select_for_update().filter(
                    pk=ancienne.centre_budgetaire_id
                ).update(**{ancien_field: F(ancien_field) - ancienne.montant_xof})

        nouveau_field = Projet.FG_DEPENSE_FIELD_MAP.get(instance.ligne_budgetaire)
        if nouveau_field:
            Projet.objects.select_for_update().filter(
                pk=instance.centre_budgetaire_id
            ).update(**{nouveau_field: F(nouveau_field) + instance.montant_xof})


@receiver(post_delete, sender=DepenseFraisGeneraux)
def restituer_budget_fg(sender, instance: DepenseFraisGeneraux, **kwargs):
    """À la suppression d'un FG, restitue le montant_xof au champ depense_fg_* du Projet."""
    field = Projet.FG_DEPENSE_FIELD_MAP.get(instance.ligne_budgetaire)
    if field:
        with transaction.atomic():
            Projet.objects.select_for_update().filter(
                pk=instance.centre_budgetaire_id
            ).update(**{field: F(field) - instance.montant_xof})
