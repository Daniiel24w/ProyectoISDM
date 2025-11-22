from django.urls import path
from . import views

app_name = 'cuotas'

urlpatterns = [
    path('generar/', views.generar_cuota_view, name='generar_cuota'),
    path('ajustes-manuales/', views.ajustes_manuales_view, name='ajustes_manuales'),

    # --- API Endpoints ---
    path('api/get-alumnos-por-plan/', views.get_alumnos_por_plan, name='get_alumnos_por_plan'),
    path('api/buscar-cuotas-alumno/', views.buscar_cuotas_alumno_api, name='buscar_cuotas_alumno_api'),
    path('api/ajustar-cuota/<int:cuota_id>/', views.ajustar_cuota_api, name='ajustar_cuota_api'),
]