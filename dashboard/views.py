"""
Tableau de bord – vues différenciées selon le rôle + page d'historique.
"""
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.mixins import ChefRequiredMixin
from depenses.models import DepenseExploitation, DepenseFraisGeneraux
from projets.models import Projet


@login_required
def accueil(request):
    if request.user.is_chef:
        return _dashboard_chef(request)
    return _dashboard_agent(request)


def _dashboard_chef(request):
    projets = list(
        Projet.objects.filter(is_active=True)
        .select_related('created_by')
        .order_by('-date_creation')
    )
    total_budget = sum(p.total_budget for p in projets)
    total_depense = sum(p.total_depense for p in projets)
    total_restant = total_budget - total_depense
    taux_global = (
        (total_depense / total_budget * 100).quantize(Decimal('0.1'))
        if total_budget else Decimal('0.0')
    )
    recentes_exploitation = (
        DepenseExploitation.objects
        .select_related('centre_budgetaire', 'created_by')
        .order_by('-date_creation')[:8]
    )
    recentes_fg = (
        DepenseFraisGeneraux.objects
        .select_related('created_by')
        .order_by('-date_creation')[:5]
    )
    projets_alerte = [p for p in projets if p.est_en_depassement]

    ctx = {
        'projets': projets,
        'projets_alerte': projets_alerte,
        'total_budget': total_budget,
        'total_depense': total_depense,
        'total_restant': total_restant,
        'taux_global': taux_global,
        'nb_projets': len(projets),
        'recentes_exploitation': recentes_exploitation,
        'recentes_fg': recentes_fg,
    }
    return render(request, 'dashboard/chef.html', ctx)


def _dashboard_agent(request):
    mes_exploitation = (
        DepenseExploitation.objects
        .filter(created_by=request.user)
        .select_related('centre_budgetaire')
        .order_by('-date_creation')[:10]
    )
    mes_fg = (
        DepenseFraisGeneraux.objects
        .filter(created_by=request.user)
        .order_by('-date_creation')[:10]
    )
    ctx = {
        'mes_exploitation': mes_exploitation,
        'mes_fg': mes_fg,
        'nb_exploitation': DepenseExploitation.objects.filter(created_by=request.user).count(),
        'nb_fg': DepenseFraisGeneraux.objects.filter(created_by=request.user).count(),
    }
    return render(request, 'dashboard/agent.html', ctx)


# ─── Historique / Audit (Chef uniquement) ─────────────────────────────────────

@login_required
def historique(request):
    if not request.user.is_chef:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    # django-simple-history génère un modèle Historical* pour chaque modèle tracé
    hist_exploitation = (
        DepenseExploitation.history
        .select_related('history_user')
        .order_by('-history_date')[:100]
    )
    hist_fg = (
        DepenseFraisGeneraux.history
        .select_related('history_user')
        .order_by('-history_date')[:100]
    )
    hist_projets = (
        Projet.history
        .select_related('history_user')
        .order_by('-history_date')[:50]
    )

    ctx = {
        'hist_exploitation': hist_exploitation,
        'hist_fg': hist_fg,
        'hist_projets': hist_projets,
    }
    return render(request, 'dashboard/historique.html', ctx)
