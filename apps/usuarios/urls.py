from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, perfil_view, registro_view

app_name = 'usuarios'

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    # La URL de logout redirigirá al usuario a la página de login.
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', perfil_view, name='perfil'),
    path('registro/', registro_view, name='registro'),
]