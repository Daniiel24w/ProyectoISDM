from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'

    def ready(self):
        # Importa el archivo de señales para que Django las reconozca
        import apps.usuarios.signals
