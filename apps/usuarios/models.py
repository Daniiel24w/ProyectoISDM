from django.db import models
from django.contrib.auth.models import User

class UserActivity(models.Model):
    """
    Modelo para registrar la actividad de inicio y cierre de sesión de los usuarios.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    login_time = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora de Ingreso")
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y Hora de Salida")

    def __str__(self):
        return f'{self.user.username} - {self.login_time.strftime("%Y-%m-%d %H:%M")}'