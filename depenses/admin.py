from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import DepenseExploitation, DepenseFraisGeneraux


class DepenseBaseAdmin(admin.ModelAdmin):
    readonly_fields = (
        'numero_saisie', 'montant_xof', 'taux_change_utilise',
        'date_creation', 'date_modification',
    )
    list_per_page = 25
    date_hierarchy = 'date_saisie'


@admin.register(DepenseExploitation)
class DepenseExploitationAdmin(DepenseBaseAdmin):
    list_display = (
        'numero_saisie', 'date_saisie', 'centre_budgetaire',
        'ligne_budgetaire', 'nature_depense', 'libelle',
        'montant', 'devise', 'montant_xof', 'fournisseur', 'created_by',
    )
    list_filter = ('ligne_budgetaire', 'nature_depense', 'devise', 'centre_budgetaire')
    search_fields = ('numero_saisie', 'libelle', 'fournisseur', 'numero_piece')
    raw_id_fields = ('centre_budgetaire', 'created_by')

    fieldsets = (
        (_("Identification"), {
            'fields': ('numero_saisie', 'date_saisie', 'centre_budgetaire', 'created_by')
        }),
        (_("Classification"), {
            'fields': ('ligne_budgetaire', 'nature_depense', 'libelle')
        }),
        (_("Montant"), {
            'fields': ('devise', 'montant', 'montant_xof', 'taux_change_utilise')
        }),
        (_("Pièce"), {
            'fields': ('fournisseur', 'numero_piece', 'piece_jointe', 'commentaire')
        }),
        (_("Dates"), {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',),
        }),
    )


@admin.register(DepenseFraisGeneraux)
class DepenseFraisGenerauxAdmin(DepenseBaseAdmin):
    list_display = (
        'numero_saisie', 'date_saisie', 'ligne_budgetaire',
        'nature_depense', 'libelle', 'montant', 'devise',
        'montant_xof', 'fournisseur', 'created_by',
    )
    list_filter = ('ligne_budgetaire', 'nature_depense', 'devise')
    search_fields = ('numero_saisie', 'libelle', 'fournisseur', 'numero_piece')
    raw_id_fields = ('created_by',)
