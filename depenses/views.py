"""
Vues Dépenses.

Règles métier :
- Création : tout utilisateur authentifié (Chef + Agent)
- Modification / Suppression : Chef uniquement
- L'agent ne voit que ses propres saisies dans sa liste
- Le chef voit toutes les saisies
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import ChefRequiredMixin
from .forms import DepenseExploitationForm, DepenseFraisGenerauxForm
from .models import DepenseExploitation, DepenseFraisGeneraux


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

        if not self.request.user.is_chef:
            qs = qs.filter(created_by=self.request.user)

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

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['lignes_choices'] = DepenseExploitation.LigneBudgetaire.choices
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
            'created_by'
        ).order_by('-date_saisie', '-date_creation')

        if not self.request.user.is_chef:
            qs = qs.filter(created_by=self.request.user)

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(libelle__icontains=q) | qs.filter(numero_saisie__icontains=q)

        ligne = self.request.GET.get('ligne', '')
        if ligne:
            qs = qs.filter(ligne_budgetaire=ligne)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['lignes_choices'] = DepenseFraisGeneraux.LigneBudgetaire.choices
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
