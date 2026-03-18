from django.apps import AppConfig


class DepensesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'depenses'
    verbose_name = 'Dépenses'

    def ready(self):
        import depenses.signals  # noqa: F401
