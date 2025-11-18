from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import UserActivity

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Crea un nuevo registro de actividad cuando un usuario inicia sesión.
    """
    UserActivity.objects.create(user=user)

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Actualiza el registro de actividad con la hora de cierre de sesión.
    Busca la última sesión abierta de ese usuario y le pone la hora de salida.
    """
    activity = UserActivity.objects.filter(user=user, logout_time__isnull=True).order_by('-login_time').first()
    if activity:
        activity.logout_time = timezone.now()
        activity.save()