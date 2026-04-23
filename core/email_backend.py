"""
Backend SMTP qui lit la configuration depuis la base de données (EmailConfig).
Fonctionne avec tous les workers Gunicorn — lit depuis la BD à chaque envoi.
Fallback automatique sur les valeurs du fichier .env si aucun enregistrement en BD.
"""
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend


class DatabaseEmailBackend(SMTPBackend):
    """
    Hérite du backend SMTP Django.
    Surcharge `open()` pour injecter les paramètres lus depuis EmailConfig.
    """

    def open(self):
        try:
            from core.models import EmailConfig
            config = EmailConfig.objects.filter(pk=1).first()
            if config and config.email_host_user:
                self.host = config.email_host
                self.port = config.email_port
                self.username = config.email_host_user
                self.password = config.email_host_password
                self.use_tls = config.email_use_tls
                self.use_ssl = config.email_use_ssl
                if config.default_from_email:
                    settings.DEFAULT_FROM_EMAIL = config.default_from_email
        except Exception:
            pass
        return super().open()
