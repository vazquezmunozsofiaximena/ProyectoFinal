# app_sabritas/apps.py
from django.apps import AppConfig

class AppSabritasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_sabritas'
    
    def ready(self):
        import app_sabritas.signals  # Registrar las señales