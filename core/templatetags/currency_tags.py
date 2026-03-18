"""
Filtres de template pour le formatage monétaire XOF.
Usage : {{ montant|xof }}  →  1 500 000 XOF
        {{ taux|pct }}      →  75,3 %
"""
from decimal import Decimal

from django import template

register = template.Library()


@register.filter(name='xof')
def format_xof(value):
    """Formate un Decimal en francs CFA : 1 500 000 XOF"""
    try:
        value = Decimal(str(value))
        # Séparateur de milliers = espace (norme française)
        int_val = int(value)
        formatted = f"{int_val:,}".replace(',', '\u202f')  # espace fine insécable
        return f"{formatted} XOF"
    except (TypeError, ValueError):
        return "— XOF"


@register.filter(name='pct')
def format_pct(value):
    """Formate un pourcentage : 75.3 → 75,3 %"""
    try:
        v = float(value)
        return f"{v:.1f} %".replace('.', ',')
    except (TypeError, ValueError):
        return "0,0 %"


@register.filter(name='pct_class')
def pct_css_class(value):
    """Retourne une classe CSS DaisyUI selon le taux de consommation."""
    try:
        v = float(value)
        if v >= 100:
            return 'progress-error'
        elif v >= 80:
            return 'progress-warning'
        elif v >= 50:
            return 'progress-info'
        return 'progress-success'
    except (TypeError, ValueError):
        return 'progress-success'


@register.filter(name='badge_montant')
def badge_montant(value):
    """Badge coloré selon si le restant est négatif."""
    try:
        v = Decimal(str(value))
        if v < 0:
            return 'badge-error'
        elif v < Decimal('100000'):
            return 'badge-warning'
        return 'badge-success'
    except (TypeError, ValueError):
        return 'badge-ghost'
