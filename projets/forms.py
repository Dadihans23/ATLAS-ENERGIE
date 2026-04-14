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
            # Exploitation
            'budget_etude', 'budget_materiel_equipement',
            'budget_logistique', 'budget_soustraitance',
            'budget_frais_mission',
            # Frais Généraux
            'budget_fg_loyers', 'budget_fg_cie', 'budget_fg_sodeci',
            'budget_fg_dotation_carburant', 'budget_fg_frais_taxi',
            'budget_fg_fournitures_bureau', 'budget_fg_produits_entretien',
            'budget_fg_assurance_sante', 'budget_fg_charges_personnel',
            'budget_fg_telephone_fixe', 'budget_fg_telephone_cellulaire',
            'budget_fg_entretien_vehicule', 'budget_fg_impots',
            'budget_fg_bic', 'budget_fg_patente',
            'budget_fg_cnps', 'budget_fg_entretien_informatique',
            'is_active',
        ]
        labels = {
            'nom': 'Nom du projet',
            'designation': 'Désignation / Description',
            'budget_etude': 'Étude',
            'budget_materiel_equipement': 'Matériel & Équipement',
            'budget_logistique': 'Logistique',
            'budget_soustraitance': 'Sous-traitance',
            'budget_frais_mission': 'Frais de Mission',
            'budget_fg_loyers': 'Loyers',
            'budget_fg_cie': 'CIE',
            'budget_fg_sodeci': 'SODECI',
            'budget_fg_dotation_carburant': 'Dotation carburant',
            'budget_fg_frais_taxi': 'Frais taxi',
            'budget_fg_fournitures_bureau': 'Fournitures bureau',
            'budget_fg_produits_entretien': 'Produits entretien & droguerie',
            'budget_fg_assurance_sante': 'Assurance santé',
            'budget_fg_charges_personnel': 'Charges personnel',
            'budget_fg_telephone_fixe': 'Téléphone fixe & internet',
            'budget_fg_telephone_cellulaire': 'Téléphone cellulaire',
            'budget_fg_entretien_vehicule': 'Entretien véhicule',
            'budget_fg_impots': 'Impôts',
            'budget_fg_bic': 'BIC',
            'budget_fg_patente': 'Patente',
            'budget_fg_cnps': 'CNPS',
            'budget_fg_entretien_informatique': 'Entretien informatique & télécom',
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
