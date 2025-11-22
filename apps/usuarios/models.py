from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    """
    Modelo que extiende el modelo User de Django para añadir campos personalizados.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono')
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name='Dirección')
    imagen = models.ImageField(
        upload_to='perfiles/', 
        default='perfiles/default-avatar.png', 
        verbose_name='Imagen de Perfil'
    )

    def __str__(self):
        return f'Perfil de {self.user.username}'

class UserActivity(models.Model):
    """
    Modelo para registrar la actividad de inicio y cierre de sesión de los usuarios.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    login_time = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora de Ingreso")
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y Hora de Salida")

    def __str__(self):
        return f'{self.user.username} - {self.login_time.strftime("%Y-%m-%d %H:%M")}'