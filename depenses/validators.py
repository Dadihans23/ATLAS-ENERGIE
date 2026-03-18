"""
Validateurs pour les pièces jointes de dépenses.
"""
import os
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_file_extension(value):
    """Vérifie que l'extension du fichier est autorisée."""
    allowed = getattr(settings, 'ALLOWED_UPLOAD_EXTENSIONS', [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png'
    ])
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in allowed:
        raise ValidationError(
            _("Extension de fichier non autorisée : %(ext)s. "
              "Extensions acceptées : %(allowed)s"),
            params={
                'ext': ext,
                'allowed': ', '.join(allowed),
            },
        )


def validate_file_size(value):
    """Vérifie que la taille du fichier ne dépasse pas la limite."""
    max_mb = getattr(settings, 'MAX_UPLOAD_SIZE_MB', 10)
    max_bytes = max_mb * 1024 * 1024
    if value.size > max_bytes:
        raise ValidationError(
            _("Fichier trop volumineux. Taille maximale autorisée : %(max)s Mo. "
              "Taille du fichier : %(size)s Mo."),
            params={
                'max': max_mb,
                'size': round(value.size / (1024 * 1024), 2),
            },
        )


def validate_montant_positif(value):
    """Vérifie que le montant est strictement positif."""
    if value <= Decimal('0.00'):
        raise ValidationError(
            _("Le montant doit être strictement positif."),
        )
