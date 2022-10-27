from django.apps import AppConfig


class B2CstaffConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'B2CStaff'

    def ready(self):
        import B2CStaff.signals
