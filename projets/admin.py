from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Projet


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('nom', 'total_budget', 'total_depense', 'budget_restant_global',
                    'taux_consommation', 'is_active', 'created_by', 'date_creation')
    list_filter = ('is_active', 'date_creation')
    search_fields = ('nom', 'designation')
    readonly_fields = (
        'depense_etude', 'depense_materiel_equipement', 'depense_logistique',
        'depense_soustraitance', 'depense_frais_mission',
        'date_creation', 'date_modification',
    )

    fieldsets = (
        (_("Identification"), {'fields': ('nom', 'designation', 'is_active', 'created_by')}),
        (_("Budgets alloués (XOF)"), {
            'fields': (
                'budget_etude', 'budget_materiel_equipement',
                'budget_logistique', 'budget_soustraitance', 'budget_frais_mission',
            )
        }),
        (_("Consommation (calculée automatiquement)"), {
            'fields': (
                'depense_etude', 'depense_materiel_equipement',
                'depense_logistique', 'depense_soustraitance', 'depense_frais_mission',
            ),
            'classes': ('collapse',),
        }),
        (_("Dates"), {'fields': ('date_creation', 'date_modification'), 'classes': ('collapse',)}),
    )
