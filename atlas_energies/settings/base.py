"""
Settings de base – partagés par tous les environnements.
"""
from pathlib import Path
from decimal import Decimal
import environ

# ─── Chemins ─────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ─── Environnement ───────────────────────────────────────────────────────────
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, [
        "atlas-energie.onrender.com"
        ]),
    SITE_ID=(int, 1),
    TAUX_EUR_XOF=(float, 655.957),
    TAUX_USD_XOF=(float, 605.00),
    MAX_UPLOAD_SIZE_MB=(int, 10),
    EMAIL_BACKEND=(str, 'core.email_backend.DatabaseEmailBackend'),
    EMAIL_HOST=(str, 'smtp.gmail.com'),
    EMAIL_PORT=(int, 587),
    EMAIL_HOST_USER=(str, ''),
    EMAIL_HOST_PASSWORD=(str, ''),
    EMAIL_USE_SSL=(bool, False),
    EMAIL_USE_TLS=(bool, True),
    DEFAULT_FROM_EMAIL=(str, 'no-reply@atlas-energies.ci'),
)
environ.Env.read_env(BASE_DIR / '.env')

# ─── Sécurité ────────────────────────────────────────────────────────────────
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# ─── Applications ─────────────────────────────────────────────────────────────
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    # Auth (social account retiré — surface d'attaque inutile)
    'allauth',
    'allauth.account',
    # Historique / audit
    'simple_history',
    # Utilitaires modèles
    'model_utils',
    # Cleanup fichiers orphelins
    'django_cleanup.apps.CleanupConfig',
    # Frontend
    'django_tables2',
    'django_filters',
    'widget_tweaks',
]

LOCAL_APPS = [
    'core.apps.CoreConfig',
    'projets.apps.ProjetsConfig',
    'depenses.apps.DepensesConfig',
    'dashboard.apps.DashboardConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─── Middleware ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'core.middleware.SecurityHeadersMiddleware',  # CSP + Permissions-Policy
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'atlas_energies.urls'

# ─── Templates ───────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.sidebar_counters',
            ],
        },
    },
]

WSGI_APPLICATION = 'atlas_energies.wsgi.application'

# ─── Base de données ─────────────────────────────────────────────────────────
DATABASES = {
    'default': env.db(default=f'sqlite:///{BASE_DIR}/db.sqlite3')
}

# ─── Modèle utilisateur personnalisé ─────────────────────────────────────────
AUTH_USER_MODEL = 'core.CustomUser'

# ─── Authentification ────────────────────────────────────────────────────────
# guardian retiré (non utilisé — surface d'attaque inutile, LOW-03)
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ─── django-allauth ──────────────────────────────────────────────────────────
SITE_ID = env('SITE_ID')
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True          # Explicite (INFORMATIONAL-04)
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = 'none'  # 'mandatory' en prod
ACCOUNT_EMAIL_NOTIFICATIONS = False  # Évite l'énumération de comptes (HIGH-03)
ACCOUNT_EMAIL_HTML = True
LOGIN_URL = '/comptes/login/'
LOGIN_REDIRECT_URL = '/tableau-de-bord/'
LOGOUT_REDIRECT_URL = '/comptes/login/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/comptes/login/'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_PASSWORD_MIN_LENGTH = 8

# Rate limiting – protège contre brute force et spam reset (CRITICAL-02)
ACCOUNT_RATE_LIMITS = {
    'login_failed':        '5/5m',   # 5 échecs par 5 minutes par email
    'login_failed_ip':     '20/5m',  # 20 échecs par 5 minutes par IP
    'signup':              '10/h',
    'password_reset':      '3/h',    # 3 demandes de reset par heure par email
    'password_reset_by_ip': '10/h',
    'email_confirmation':  '5/h',
}

# ─── Validation mots de passe ────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Internationalisation ─────────────────────────────────────────────────────
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

# ─── Sessions (MEDIUM-03) ─────────────────────────────────────────────────────
SESSION_COOKIE_AGE = 28800              # 8 heures (journée de travail)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Expire à fermeture du navigateur
SESSION_SAVE_EVERY_REQUEST = True       # Renouvelle à chaque requête active

# ─── Cookies sécurisés ────────────────────────────────────────────────────────
# Lax (pas Strict) : SameSite=Strict bloque le cookie sur les redirects de
# navigation externe (ex: clic depuis un client email → reset password),
# ce qui casse le flow allauth reset_password_from_key.
# SameSite=Lax protège quand même contre les CSRF cross-site POST.
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# ─── Fichiers statiques ───────────────────────────────────────────────────────
STATIC_URL = env('STATIC_URL', default='/static/')
STATIC_ROOT = BASE_DIR / env('STATIC_ROOT', default='staticfiles')
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ─── Fichiers médias ─────────────────────────────────────────────────────────
MEDIA_URL = env('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / env('MEDIA_ROOT', default='media')

# ─── Email ───────────────────────────────────────────────────────────────────
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_SSL = env('EMAIL_USE_SSL')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

# ─── Clé primaire par défaut ──────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── django-tables2 ──────────────────────────────────────────────────────────
DJANGO_TABLES2_TEMPLATE = 'django_tables2/bootstrap5.html'

# ─── django-simple-history ───────────────────────────────────────────────────
SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD = True

# ─── Taux de change ──────────────────────────────────────────────────────────
TAUX_EUR_XOF = Decimal(str(env('TAUX_EUR_XOF')))
TAUX_USD_XOF = Decimal(str(env('TAUX_USD_XOF')))

# ─── Upload fichiers ─────────────────────────────────────────────────────────
MAX_UPLOAD_SIZE_MB = env('MAX_UPLOAD_SIZE_MB')
ALLOWED_UPLOAD_EXTENSIONS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png']

# ─── Logs de sécurité (MEDIUM-07) ────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'security': {
            'format': '[SECURITY] {asctime} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'security',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security_console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
