"""
Settings package – charge dev par défaut.
En production : DJANGO_SETTINGS_MODULE=atlas_energies.settings.prod
"""
from .dev import *  # noqa: F401, F403
