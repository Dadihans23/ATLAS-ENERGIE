"""
Settings de développement.
"""
from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0','atlas-energie.onrender.com']

# Vérification email désactivée en dev
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Logs : uniquement les erreurs (plus de spam SQL dans le terminal)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'ERROR',   # était DEBUG → affichait chaque requête SQL
        },
    },
}
