"""
Context processors — injectés dans tous les templates.
Fournit les compteurs d'alertes selon le rôle de l'utilisateur connecté.
"""
from depenses.models import DepenseExploitation, DepenseFraisGeneraux, StatutDepense


def sidebar_counters(request):
    """
    Injecte les compteurs d'alertes dans tous les templates.
    N'exécute des requêtes que si l'utilisateur est connecté.
    """
    if not request.user.is_authenticated:
        return {}

    u = request.user
    ctx = {
        'nb_attente_dg': 0,
        'nb_attente_dt': 0,
        'nb_attente_df': 0,
        'nb_a_decaisser': 0,
    }

    if u.is_chef:
        ctx['nb_attente_dg'] = (
            DepenseExploitation.objects.filter(statut=StatutDepense.APPROUVE_N1).count()
            + DepenseFraisGeneraux.objects.filter(statut=StatutDepense.APPROUVE_N1).count()
        )

    elif u.is_dt:
        ctx['nb_attente_dt'] = DepenseExploitation.objects.filter(
            statut=StatutDepense.SOUMIS
        ).count()

    elif u.is_df:
        ctx['nb_attente_df'] = DepenseFraisGeneraux.objects.filter(
            statut=StatutDepense.SOUMIS
        ).count()

    elif u.is_agent:
        ctx['nb_a_decaisser'] = (
            DepenseExploitation.objects.filter(statut=StatutDepense.APPROUVE_DG).count()
            + DepenseFraisGeneraux.objects.filter(statut=StatutDepense.APPROUVE_DG).count()
        )

    return ctx
