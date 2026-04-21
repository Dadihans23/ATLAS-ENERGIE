"""
Settings de production – sécurité renforcée.
"""
from .base import *  # noqa: F401, F403

DEBUG = False

# ─── HTTPS / Cookies sécurisés ───────────────────────────────────────────────
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
# X-XSS-Protection désactivé (déprécié depuis Chrome 78, peut créer des vulns - LOW-01)
SECURE_BROWSER_XSS_FILTER = False

# ─── SSL — à activer une fois le certificat Let's Encrypt en place ────────────
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
# SECURE_HSTS_SECONDS = 31536000      # à décommenter après SSL
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# ─── Origines CSRF autorisées ────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [
    'http://atlasenergies.net',
    'http://www.atlasenergies.net',
    'http://79.143.190.190',
]

# ─── Email (HIGH-04) ─────────────────────────────────────────────────────────
# Toute la config email est lue depuis .env via base.py
# Ne pas surcharger EMAIL_PORT / EMAIL_USE_TLS ici → incohérence SSL/TLS
# Activer la vérification email en prod
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

# ─── Allauth production (MEDIUM-05) ──────────────────────────────────────────
# Force les liens de reset en HTTPS
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# ─── Logs production ─────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'security': {
            'format': '[SECURITY] {asctime} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django_errors.log',  # noqa: F405
            'formatter': 'verbose',
        },
        'file_security': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/security.log',  # noqa: F405
            'formatter': 'security',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['file_security'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['file_errors'],
        'level': 'ERROR',
    },
}
