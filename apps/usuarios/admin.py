from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Perfil, UserActivity

# Define un admin inline para el modelo Perfil
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'perfiles'

# Extiende el UserAdmin para incluir el Perfil
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)

# Vuelve a registrar el User admin con la nueva configuración
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(UserActivity)