"""
Formulaires de dépenses.
- DepenseExploitationForm : tous les utilisateurs authentifiés
- DepenseFraisGenerauxForm : tous les utilisateurs authentifiés
"""
from django import forms

from projets.models import Projet
from .models import DepenseExploitation, DepenseFraisGeneraux


class DepenseExploitationForm(forms.ModelForm):
    class Meta:
        model = DepenseExploitation
        fields = [
            'date_saisie', 'centre_budgetaire', 'ligne_budgetaire',
            'nature_depense', 'libelle', 'devise', 'montant',
            'fournisseur', 'numero_piece', 'piece_jointe', 'commentaire',
        ]
        labels = {
            'date_saisie': 'Date de saisie',
            'centre_budgetaire': 'Projet (centre budgétaire)',
            'ligne_budgetaire': 'Ligne budgétaire',
            'nature_depense': 'Nature de la dépense',
            'libelle': 'Libellé',
            'devise': 'Devise',
            'montant': 'Montant',
            'fournisseur': 'Fournisseur',
            'numero_piece': 'N° de pièce',
            'piece_jointe': 'Pièce jointe',
            'commentaire': 'Commentaire',
        }
        widgets = {
            'date_saisie': forms.DateInput(attrs={'type': 'date'}),
            'libelle': forms.Textarea(attrs={'rows': 2}),
            'commentaire': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limiter aux projets actifs
        self.fields['centre_budgetaire'].queryset = Projet.objects.filter(is_active=True)


class DepenseFraisGenerauxForm(forms.ModelForm):
    class Meta:
        model = DepenseFraisGeneraux
        fields = [
            'date_saisie', 'centre_budgetaire', 'ligne_budgetaire', 'nature_depense',
            'libelle', 'devise', 'montant',
            'fournisseur', 'numero_piece', 'piece_jointe', 'commentaire',
        ]
        labels = {
            'date_saisie': 'Date de saisie',
            'centre_budgetaire': 'Projet',
            'ligne_budgetaire': 'Ligne budgétaire',
            'nature_depense': 'Nature de la dépense',
            'libelle': 'Libellé',
            'devise': 'Devise',
            'montant': 'Montant',
            'fournisseur': 'Fournisseur',
            'numero_piece': 'N° de pièce',
            'piece_jointe': 'Pièce jointe',
            'commentaire': 'Commentaire',
        }
        widgets = {
            'date_saisie': forms.DateInput(attrs={'type': 'date'}),
            'libelle': forms.Textarea(attrs={'rows': 2}),
            'commentaire': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['centre_budgetaire'].queryset = Projet.objects.filter(is_active=True)
