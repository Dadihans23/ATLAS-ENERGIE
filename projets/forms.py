"""
Formulaires Projet – uniquement accessibles au Chef d'Agence.
"""
from django import forms

from .models import Projet


class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = [
            'nom', 'designation',
            'budget_etude', 'budget_materiel_equipement',
            'budget_logistique', 'budget_soustraitance',
            'budget_frais_mission', 'is_active',
        ]
        labels = {
            'nom': 'Nom du projet',
            'designation': 'Désignation / Description',
            'budget_etude': 'Budget Étude (XOF)',
            'budget_materiel_equipement': 'Budget Matériel & Équipement (XOF)',
            'budget_logistique': 'Budget Logistique (XOF)',
            'budget_soustraitance': 'Budget Sous-traitance (XOF)',
            'budget_frais_mission': 'Budget Frais de Mission (XOF)',
            'is_active': 'Projet actif',
        }
        widgets = {
            'designation': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_nom(self):
        nom = self.cleaned_data.get('nom', '').strip()
        if not nom:
            raise forms.ValidationError("Le nom du projet est obligatoire.")
        return nom
