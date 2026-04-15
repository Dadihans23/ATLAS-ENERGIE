"""
Vues Projet – réservées au Chef d'Agence (CRUD complet).
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.mixins import ChefRequiredMixin
from .forms import ProjetForm
from .models import Projet


class ProjetListView(LoginRequiredMixin, ListView):
    model = Projet
    template_name = 'projets/liste.html'
    context_object_name = 'projets'
    paginate_by = 20

    def get_queryset(self):
        qs = Projet.objects.select_related('created_by').order_by('-date_creation')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(nom__icontains=q)
        actif = self.request.GET.get('actif', '')
        if actif == '1':
            qs = qs.filter(is_active=True)
        elif actif == '0':
            qs = qs.filter(is_active=False)
        return qs


class ProjetDetailView(LoginRequiredMixin, DetailView):
    model = Projet
    template_name = 'projets/detail.html'
    context_object_name = 'projet'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        projet = self.object
        ctx['depenses'] = (
            projet.depenses_exploitation
            .select_related('created_by')
            .order_by('-date_saisie')[:50]
        )
        ctx['depenses_fg'] = (
            projet.depenses_frais_generaux
            .select_related('created_by')
            .order_by('-date_saisie')[:50]
        )
        def _taux(budget, depense):
            from decimal import Decimal
            if not budget:
                return Decimal('0.00')
            return (depense / budget * 100).quantize(Decimal('0.01'))

        ctx['lignes'] = [
            {
                'label': 'Étude',
                'budget': projet.budget_etude,
                'depense': projet.depense_etude,
                'restant': projet.restant_etude,
                'taux': _taux(projet.budget_etude, projet.depense_etude),
            },
            {
                'label': 'Matériel & Équipement',
                'budget': projet.budget_materiel_equipement,
                'depense': projet.depense_materiel_equipement,
                'restant': projet.restant_materiel_equipement,
                'taux': _taux(projet.budget_materiel_equipement, projet.depense_materiel_equipement),
            },
            {
                'label': 'Logistique',
                'budget': projet.budget_logistique,
                'depense': projet.depense_logistique,
                'restant': projet.restant_logistique,
                'taux': _taux(projet.budget_logistique, projet.depense_logistique),
            },
            {
                'label': 'Sous-traitance',
                'budget': projet.budget_soustraitance,
                'depense': projet.depense_soustraitance,
                'restant': projet.restant_soustraitance,
                'taux': _taux(projet.budget_soustraitance, projet.depense_soustraitance),
            },
            {
                'label': 'Frais de Mission',
                'budget': projet.budget_frais_mission,
                'depense': projet.depense_frais_mission,
                'restant': projet.restant_frais_mission,
                'taux': _taux(projet.budget_frais_mission, projet.depense_frais_mission),
            },
        ]

        fg_definitions = [
            ('Loyers', 'loyers'),
            ('CIE', 'cie'),
            ('SODECI', 'sodeci'),
            ('Dotation carburant', 'dotation_carburant'),
            ('Frais taxi', 'frais_taxi'),
            ('Fournitures bureau', 'fournitures_bureau'),
            ('Produits entretien & droguerie', 'produits_entretien'),
            ('Assurance santé', 'assurance_sante'),
            ('Charges personnel', 'charges_personnel'),
            ('Téléphone fixe & internet', 'telephone_fixe'),
            ('Téléphone cellulaire', 'telephone_cellulaire'),
            ('Entretien véhicule', 'entretien_vehicule'),
            ('Impôts', 'impots'),
            ('BIC', 'bic'),
            ('Patente', 'patente'),
            ('CNPS', 'cnps'),
            ('Entretien informatique & télécom', 'entretien_informatique'),
        ]
        ctx['lignes_fg'] = [
            {
                'label': label,
                'budget': getattr(projet, f'budget_fg_{key}'),
                'depense': getattr(projet, f'depense_fg_{key}'),
                'restant': getattr(projet, f'budget_fg_{key}') - getattr(projet, f'depense_fg_{key}'),
                'taux': _taux(getattr(projet, f'budget_fg_{key}'), getattr(projet, f'depense_fg_{key}')),
            }
            for label, key in fg_definitions
        ]
        return ctx


class ProjetCreateView(ChefRequiredMixin, CreateView):
    model = Projet
    form_class = ProjetForm
    template_name = 'projets/form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre'] = 'Nouveau projet'
        ctx['action_url'] = reverse('projets:creer')
        ctx['retour_url'] = reverse('projets:liste')
        return ctx

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.save()
        messages.success(self.request, f"Projet « {form.instance.nom} » créé avec succès.")
        return redirect('projets:liste')


class ProjetUpdateView(ChefRequiredMixin, UpdateView):
    model = Projet
    form_class = ProjetForm
    template_name = 'projets/form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre'] = f'Modifier — {self.object.nom}'
        ctx['action_url'] = reverse('projets:modifier', kwargs={'pk': self.object.pk})
        ctx['retour_url'] = reverse('projets:liste')
        return ctx

    def form_valid(self, form):
        form.save()
        messages.success(self.request, f"Projet « {form.instance.nom} » mis à jour.")
        return redirect('projets:liste')


class ProjetDeleteView(ChefRequiredMixin, DeleteView):
    model = Projet
    template_name = 'projets/confirm_delete.html'
    success_url = reverse_lazy('projets:liste')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['objet_nom'] = self.object.nom
        ctx['retour_url'] = reverse('projets:liste')
        # Compte toutes les dépenses (y compris déjà archivées éventuellement)
        ctx['nb_exp'] = self.object.depenses_exploitation.count()
        ctx['nb_fg'] = self.object.depenses_frais_generaux.count()
        return ctx

    def form_valid(self, form):
        nom = self.object.nom
        now = timezone.now()
        # Soft-delete en cascade sur toutes les dépenses du projet
        nb_exp = self.object.depenses_exploitation.update(is_deleted=True, deleted_at=now)
        nb_fg = self.object.depenses_frais_generaux.update(is_deleted=True, deleted_at=now)
        # Soft-delete du projet lui-même
        self.object.is_deleted = True
        self.object.deleted_at = now
        self.object.is_active = False
        self.object.save(update_fields=['is_deleted', 'deleted_at', 'is_active'])
        messages.success(
            self.request,
            f"Projet « {nom} » archivé avec {nb_exp} dépense(s) d'exploitation "
            f"et {nb_fg} frais généraux."
        )
        return redirect(self.success_url)
