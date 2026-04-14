"""
Vues Dépenses + Workflow de validation.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.mixins import ChefRequiredMixin
from .forms import DepenseExploitationForm, DepenseFraisGenerauxForm
from .models import DepenseExploitation, DepenseFraisGeneraux, StatutDepense


# ─── Dépenses d'exploitation ──────────────────────────────────────────────────

class DepenseExploitationListView(LoginRequiredMixin, ListView):
    model = DepenseExploitation
    template_name = 'depenses/liste_exploitation.html'
    context_object_name = 'depenses'
    paginate_by = 25

    def get_queryset(self):
        qs = DepenseExploitation.objects.select_related(
            'centre_budgetaire', 'created_by'
        ).order_by('-date_saisie', '-date_creation')

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(libelle__icontains=q) | qs.filter(numero_saisie__icontains=q)

        projet_id = self.request.GET.get('projet', '')
        if projet_id:
            try:
                qs = qs.filter(centre_budgetaire_id=int(projet_id))
            except (ValueError, TypeError):
                pass

        ligne = self.request.GET.get('ligne', '')
        if ligne:
            qs = qs.filter(ligne_budgetaire=ligne)

        statut = self.request.GET.get('statut', '')
        if statut:
            qs = qs.filter(statut=statut)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['lignes_choices'] = DepenseExploitation.LigneBudgetaire.choices
        ctx['statut_choices'] = StatutDepense.choices
        return ctx


class DepenseExploitationCreateView(LoginRequiredMixin, CreateView):
    model = DepenseExploitation
    form_class = DepenseExploitationForm
    template_name = 'depenses/form_exploitation.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre'] = "Nouvelle dépense d'exploitation"
        ctx['action_url'] = reverse('depenses:exploitation_creer')
        ctx['retour_url'] = reverse('depenses:exploitation_liste')
        return ctx

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.save()
        messages.success(
            self.request,
            f"Dépense {form.instance.numero_saisie} enregistrée avec succès."
        )
        return redirect('depenses:exploitation_liste')


class DepenseExploitationDetailView(LoginRequiredMixin, DetailView):
    model = DepenseExploitation
    template_name = 'depenses/detail_exploitation.html'
    context_object_name = 'depense'

    def get_queryset(self):
        return DepenseExploitation.objects.select_related(
            'centre_budgetaire', 'created_by',
            'valide_par_n1', 'valide_par_dg', 'decaisse_par'
        )


class DepenseExploitationUpdateView(ChefRequiredMixin, UpdateView):
    model = DepenseExploitation
    form_class = DepenseExploitationForm
    template_name = 'depenses/form_exploitation.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre'] = f"Modifier — {self.object.numero_saisie}"
        ctx['action_url'] = reverse('depenses:exploitation_modifier', kwargs={'pk': self.object.pk})
        ctx['retour_url'] = reverse('depenses:exploitation_liste')
        return ctx

    def form_valid(self, form):
        form.save()
        messages.success(self.request, f"Dépense {form.instance.numero_saisie} mise à jour.")
        return redirect('depenses:exploitation_liste')


class DepenseExploitationDeleteView(ChefRequiredMixin, DeleteView):
    model = DepenseExploitation
    template_name = 'depenses/confirm_delete.html'
    success_url = reverse_lazy('depenses:exploitation_liste')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['objet_nom'] = self.object.numero_saisie
        ctx['retour_url'] = reverse('depenses:exploitation_liste')
        return ctx

    def form_valid(self, form):
        num = self.object.numero_saisie
        self.object.delete()
        messages.success(self.request, f"Dépense {num} supprimée.")
        return redirect(self.success_url)


# ─── Frais généraux ───────────────────────────────────────────────────────────

class DepenseFraisGenerauxListView(LoginRequiredMixin, ListView):
    model = DepenseFraisGeneraux
    template_name = 'depenses/liste_frais_generaux.html'
    context_object_name = 'depenses'
    paginate_by = 25

    def get_queryset(self):
        qs = DepenseFraisGeneraux.objects.select_related(
            'centre_budgetaire', 'created_by'
        ).order_by('-date_saisie', '-date_creation')

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(libelle__icontains=q) | qs.filter(numero_saisie__icontains=q)

        projet_id = self.request.GET.get('projet', '')
        if projet_id:
            try:
                qs = qs.filter(centre_budgetaire_id=int(projet_id))
            except (ValueError, TypeError):
                pass

        ligne = self.request.GET.get('ligne', '')
        if ligne:
            qs = qs.filter(ligne_budgetaire=ligne)

        statut = self.request.GET.get('statut', '')
        if statut:
            qs = qs.filter(statut=statut)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['lignes_choices'] = DepenseFraisGeneraux.LigneBudgetaire.choices
        ctx['statut_choices'] = StatutDepense.choices
        return ctx


class DepenseFraisGenerauxCreateView(LoginRequiredMixin, CreateView):
    model = DepenseFraisGeneraux
    form_class = DepenseFraisGenerauxForm
    template_name = 'depenses/form_frais_generaux.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre'] = "Nouveau frais général"
        ctx['action_url'] = reverse('depenses:fg_creer')
        ctx['retour_url'] = reverse('depenses:fg_liste')
        return ctx

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.save()
        messages.success(
            self.request,
            f"Frais général {form.instance.numero_saisie} enregistré avec succès."
        )
        return redirect('depenses:fg_liste')


class DepenseFraisGenerauxDetailView(LoginRequiredMixin, DetailView):
    model = DepenseFraisGeneraux
    template_name = 'depenses/detail_frais_generaux.html'
    context_object_name = 'depense'

    def get_queryset(self):
        return DepenseFraisGeneraux.objects.select_related(
            'centre_budgetaire', 'created_by',
            'valide_par_n1', 'valide_par_dg', 'decaisse_par'
        )


class DepenseFraisGenerauxUpdateView(ChefRequiredMixin, UpdateView):
    model = DepenseFraisGeneraux
    form_class = DepenseFraisGenerauxForm
    template_name = 'depenses/form_frais_generaux.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre'] = f"Modifier — {self.object.numero_saisie}"
        ctx['action_url'] = reverse('depenses:fg_modifier', kwargs={'pk': self.object.pk})
        ctx['retour_url'] = reverse('depenses:fg_liste')
        return ctx

    def form_valid(self, form):
        form.save()
        messages.success(self.request, f"Frais {form.instance.numero_saisie} mis à jour.")
        return redirect('depenses:fg_liste')


class DepenseFraisGenerauxDeleteView(ChefRequiredMixin, DeleteView):
    model = DepenseFraisGeneraux
    template_name = 'depenses/confirm_delete.html'
    success_url = reverse_lazy('depenses:fg_liste')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['objet_nom'] = self.object.numero_saisie
        ctx['retour_url'] = reverse('depenses:fg_liste')
        return ctx

    def form_valid(self, form):
        num = self.object.numero_saisie
        self.object.delete()
        messages.success(self.request, f"Frais {num} supprimé.")
        return redirect(self.success_url)


# ═══════════════════════════════════════════════════════════════════════════════
# Workflow de validation
# ═══════════════════════════════════════════════════════════════════════════════

def _get_depense(type_depense, pk):
    """Retourne la dépense (exploitation ou fg) ou 404."""
    if type_depense == 'exploitation':
        return get_object_or_404(DepenseExploitation, pk=pk)
    return get_object_or_404(DepenseFraisGeneraux, pk=pk)


def _retour_liste(type_depense):
    if type_depense == 'exploitation':
        return reverse('depenses:exploitation_liste')
    return reverse('depenses:fg_liste')


def approuver_n1(request, type_depense, pk):
    """DT approuve une exploitation / DF approuve un FG."""
    user = request.user
    if not user.is_authenticated:
        raise PermissionDenied
    if type_depense == 'exploitation' and not user.is_dt:
        raise PermissionDenied
    if type_depense == 'fg' and not user.is_df:
        raise PermissionDenied

    depense = _get_depense(type_depense, pk)
    if depense.statut != StatutDepense.SOUMIS:
        messages.error(request, "Cette dépense ne peut pas être approuvée dans son état actuel.")
        return redirect(_retour_liste(type_depense))

    depense.statut = StatutDepense.APPROUVE_N1
    depense.valide_par_n1 = user
    depense.date_validation_n1 = timezone.now()
    depense.motif_rejet_n1 = ''
    depense.save(update_fields=['statut', 'valide_par_n1', 'date_validation_n1', 'motif_rejet_n1'])
    messages.success(request, f"Dépense {depense.numero_saisie} approuvée. Le DG a été notifié.")
    return redirect(_retour_liste(type_depense))


def rejeter_n1(request, type_depense, pk):
    """DT rejette une exploitation / DF rejette un FG avec motif."""
    user = request.user
    if not user.is_authenticated:
        raise PermissionDenied
    if type_depense == 'exploitation' and not user.is_dt:
        raise PermissionDenied
    if type_depense == 'fg' and not user.is_df:
        raise PermissionDenied

    depense = _get_depense(type_depense, pk)
    if request.method == 'POST':
        motif = request.POST.get('motif', '').strip()
        if not motif:
            messages.error(request, "Veuillez saisir un motif de rejet.")
            return render(request, 'depenses/rejet_form.html', {
                'depense': depense, 'type_depense': type_depense,
                'action_url': request.path,
            })
        depense.statut = StatutDepense.REJETE
        depense.valide_par_n1 = user
        depense.date_validation_n1 = timezone.now()
        depense.motif_rejet_n1 = motif
        depense.save(update_fields=['statut', 'valide_par_n1', 'date_validation_n1', 'motif_rejet_n1'])
        messages.success(request, f"Dépense {depense.numero_saisie} rejetée.")
        return redirect(_retour_liste(type_depense))

    return render(request, 'depenses/rejet_form.html', {
        'depense': depense, 'type_depense': type_depense,
        'action_url': request.path,
    })


def approuver_dg(request, type_depense, pk):
    """DG donne l'approbation finale."""
    if not request.user.is_authenticated or not request.user.is_chef:
        raise PermissionDenied

    depense = _get_depense(type_depense, pk)
    if depense.statut != StatutDepense.APPROUVE_N1:
        messages.error(request, "Cette dépense n'est pas en attente d'approbation DG.")
        return redirect(_retour_liste(type_depense))

    depense.statut = StatutDepense.APPROUVE_DG
    depense.valide_par_dg = request.user
    depense.date_validation_dg = timezone.now()
    depense.motif_rejet_dg = ''
    depense.save(update_fields=['statut', 'valide_par_dg', 'date_validation_dg', 'motif_rejet_dg'])
    messages.success(request, f"Dépense {depense.numero_saisie} approuvée définitivement. L'agent peut procéder au décaissement.")
    return redirect(_retour_liste(type_depense))


def rejeter_dg(request, type_depense, pk):
    """DG rejette → repart en circuit (statut = soumis)."""
    if not request.user.is_authenticated or not request.user.is_chef:
        raise PermissionDenied

    depense = _get_depense(type_depense, pk)
    if request.method == 'POST':
        motif = request.POST.get('motif', '').strip()
        if not motif:
            messages.error(request, "Veuillez saisir un motif de rejet.")
            return render(request, 'depenses/rejet_form.html', {
                'depense': depense, 'type_depense': type_depense,
                'action_url': request.path, 'is_dg': True,
            })
        # Repart en circuit depuis le début
        depense.statut = StatutDepense.SOUMIS
        depense.valide_par_dg = request.user
        depense.date_validation_dg = timezone.now()
        depense.motif_rejet_dg = motif
        # Réinitialise la validation N1
        depense.valide_par_n1 = None
        depense.date_validation_n1 = None
        depense.motif_rejet_n1 = ''
        depense.save(update_fields=[
            'statut', 'valide_par_dg', 'date_validation_dg', 'motif_rejet_dg',
            'valide_par_n1', 'date_validation_n1', 'motif_rejet_n1',
        ])
        messages.warning(request, f"Dépense {depense.numero_saisie} renvoyée en circuit (motif notifié).")
        return redirect(_retour_liste(type_depense))

    return render(request, 'depenses/rejet_form.html', {
        'depense': depense, 'type_depense': type_depense,
        'action_url': request.path, 'is_dg': True,
    })


def decaissements(request):
    """Liste des dépenses approuvées DG — vue agent pour décaissement."""
    if not request.user.is_authenticated:
        raise PermissionDenied

    exp = DepenseExploitation.objects.filter(
        statut=StatutDepense.APPROUVE_DG
    ).select_related('centre_budgetaire', 'created_by').order_by('-date_validation_dg')

    fg = DepenseFraisGeneraux.objects.filter(
        statut=StatutDepense.APPROUVE_DG
    ).select_related('centre_budgetaire', 'created_by').order_by('-date_validation_dg')

    return render(request, 'depenses/decaissements.html', {
        'depenses_exp': exp,
        'depenses_fg': fg,
    })


def decaisser(request, type_depense, pk):
    """Agent marque une dépense comme décaissée."""
    if not request.user.is_authenticated:
        raise PermissionDenied

    depense = _get_depense(type_depense, pk)
    if depense.statut != StatutDepense.APPROUVE_DG:
        messages.error(request, "Cette dépense n'est pas prête pour le décaissement.")
        return redirect('depenses:decaissements')

    depense.statut = StatutDepense.DECAISSE
    depense.decaisse_par = request.user
    depense.date_decaissement = timezone.now()
    depense.save(update_fields=['statut', 'decaisse_par', 'date_decaissement'])
    messages.success(request, f"Dépense {depense.numero_saisie} décaissée avec succès.")
    return redirect('depenses:decaissements')
