from django.apps import AppConfig


class AlexanderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alexander'


    def ready(self):
        import alexander.signals