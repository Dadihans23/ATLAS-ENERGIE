"""
Tableau de bord – vues différenciées selon le rôle + page d'historique.
"""
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.mixins import ChefRequiredMixin
from depenses.models import DepenseExploitation, DepenseFraisGeneraux, StatutDepense
from projets.models import Projet


@login_required
def accueil(request):
    if request.user.is_chef:
        return _dashboard_chef(request)
    if request.user.is_dt:
        return _dashboard_directeur(request, 'technique')
    if request.user.is_df:
        return _dashboard_directeur(request, 'financier')
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
        .select_related('centre_budgetaire', 'created_by')
        .order_by('-date_creation')[:5]
    )
    projets_alerte = [p for p in projets if p.est_en_depassement]

    # Badge DG : dépenses en attente d'approbation DG
    nb_attente_dg = (
        DepenseExploitation.objects.filter(statut=StatutDepense.APPROUVE_N1).count()
        + DepenseFraisGeneraux.objects.filter(statut=StatutDepense.APPROUVE_N1).count()
    )

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
        'nb_attente_dg': nb_attente_dg,
    }
    return render(request, 'dashboard/chef.html', ctx)


def _dashboard_directeur(request, type_dir):
    """Dashboard commun DT et DF — similaire au chef sans volet administration."""
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

    if type_dir == 'technique':
        # DT : dépenses exploitation à valider
        a_valider = (
            DepenseExploitation.objects
            .filter(statut=StatutDepense.SOUMIS)
            .select_related('centre_budgetaire', 'created_by')
            .order_by('-date_creation')[:10]
        )
        recentes = (
            DepenseExploitation.objects
            .select_related('centre_budgetaire', 'created_by')
            .order_by('-date_creation')[:8]
        )
        nb_a_valider = DepenseExploitation.objects.filter(statut=StatutDepense.SOUMIS).count()
        template = 'dashboard/directeur_technique.html'
    else:
        # DF : dépenses FG à valider
        a_valider = (
            DepenseFraisGeneraux.objects
            .filter(statut=StatutDepense.SOUMIS)
            .select_related('centre_budgetaire', 'created_by')
            .order_by('-date_creation')[:10]
        )
        recentes = (
            DepenseFraisGeneraux.objects
            .select_related('centre_budgetaire', 'created_by')
            .order_by('-date_creation')[:8]
        )
        nb_a_valider = DepenseFraisGeneraux.objects.filter(statut=StatutDepense.SOUMIS).count()
        template = 'dashboard/directeur_financier.html'

    projets_alerte = [p for p in projets if p.est_en_depassement]
    ctx = {
        'projets': projets,
        'projets_alerte': projets_alerte,
        'total_budget': total_budget,
        'total_depense': total_depense,
        'total_restant': total_restant,
        'taux_global': taux_global,
        'nb_projets': len(projets),
        'a_valider': a_valider,
        'nb_a_valider': nb_a_valider,
        'recentes': recentes,
    }
    return render(request, template, ctx)


def _dashboard_agent(request):
    projets = list(
        Projet.objects.filter(is_active=True)
        .select_related('created_by')
        .order_by('-date_creation')
    )
    recentes_exploitation = (
        DepenseExploitation.objects
        .select_related('centre_budgetaire', 'created_by')
        .order_by('-date_creation')[:10]
    )
    recentes_fg = (
        DepenseFraisGeneraux.objects
        .select_related('centre_budgetaire', 'created_by')
        .order_by('-date_creation')[:10]
    )
    ctx = {
        'projets': projets,
        'nb_projets': len(projets),
        'recentes_exploitation': recentes_exploitation,
        'recentes_fg': recentes_fg,
        'nb_exploitation': DepenseExploitation.objects.count(),
        'nb_fg': DepenseFraisGeneraux.objects.count(),
    }
    return render(request, 'dashboard/agent.html', ctx)


# ─── Suivi complet (Chef/DG uniquement) ──────────────────────────────────────

@login_required
def suivi(request):
    if not request.user.is_chef:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    tab = request.GET.get('tab', 'approuves_n1')

    approuves_n1_exp = (
        DepenseExploitation.objects
        .filter(statut=StatutDepense.APPROUVE_N1)
        .select_related('centre_budgetaire', 'created_by', 'valide_par_n1')
        .order_by('-date_validation_n1')
    )
    approuves_n1_fg = (
        DepenseFraisGeneraux.objects
        .filter(statut=StatutDepense.APPROUVE_N1)
        .select_related('centre_budgetaire', 'created_by', 'valide_par_n1')
        .order_by('-date_validation_n1')
    )
    approuves_dg_exp = (
        DepenseExploitation.objects
        .filter(statut__in=[StatutDepense.APPROUVE_DG, StatutDepense.DECAISSE])
        .select_related('centre_budgetaire', 'created_by', 'valide_par_dg')
        .order_by('-date_validation_dg')
    )
    approuves_dg_fg = (
        DepenseFraisGeneraux.objects
        .filter(statut__in=[StatutDepense.APPROUVE_DG, StatutDepense.DECAISSE])
        .select_related('centre_budgetaire', 'created_by', 'valide_par_dg')
        .order_by('-date_validation_dg')
    )
    decaisses_exp = (
        DepenseExploitation.objects
        .filter(statut=StatutDepense.DECAISSE)
        .select_related('centre_budgetaire', 'created_by', 'decaisse_par')
        .order_by('-date_decaissement')
    )
    decaisses_fg = (
        DepenseFraisGeneraux.objects
        .filter(statut=StatutDepense.DECAISSE)
        .select_related('centre_budgetaire', 'created_by', 'decaisse_par')
        .order_by('-date_decaissement')
    )

    ctx = {
        'tab': tab,
        'approuves_n1_exp': approuves_n1_exp,
        'approuves_n1_fg': approuves_n1_fg,
        'approuves_dg_exp': approuves_dg_exp,
        'approuves_dg_fg': approuves_dg_fg,
        'decaisses_exp': decaisses_exp,
        'decaisses_fg': decaisses_fg,
        'nb_n1': approuves_n1_exp.count() + approuves_n1_fg.count(),
        'nb_dg': approuves_dg_exp.count() + approuves_dg_fg.count(),
        'nb_decaisses': decaisses_exp.count() + decaisses_fg.count(),
    }
    return render(request, 'dashboard/suivi.html', ctx)


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
