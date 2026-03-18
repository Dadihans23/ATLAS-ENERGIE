"""
Settings de développement.
"""
from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Debug toolbar
INSTALLED_APPS += ['debug_toolbar']  # noqa: F405
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE  # noqa: F405
INTERNAL_IPS = ['127.0.0.1']

# Email → SMTP Gmail (les credentials viennent du .env)
# Pour tester sans envoyer de vrais mails, commenter la ligne ci-dessous
# et décommenter : EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Vérification email désactivée en dev
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Logs SQL en dev
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
