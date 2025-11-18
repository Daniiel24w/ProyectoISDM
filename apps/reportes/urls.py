from django.urls import path
from .views import lista_reportes_view, lotes_data_ajax

app_name = 'reportes'

urlpatterns = [
    # URL para la página principal que muestra la tabla
    path('', lista_reportes_view, name='lista_reportes'),
    # URL para la data en formato JSON que consumirá DataTables
    path('data/', lotes_data_ajax, name='lotes_data_ajax'),
]