from django.urls import path
from . import views

app_name = 'cuotas'

urlpatterns = [
    path('generar/', views.generar_cuota_view, name='generar_cuota'), # URL final: /cuotas/generar/
    path('ajustes-manuales/', views.ajustes_manuales_view, name='ajustes_manuales'), # URL final: /cuotas/ajustes-manuales/
]