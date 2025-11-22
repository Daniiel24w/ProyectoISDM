from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.lista_reportes_view, name='lista_reportes'),
    # URL para que DataTables obtenga los datos de los lotes
    path('api/lotes-data/', views.lotes_data_ajax, name='lotes_data_ajax'),
    # URL para anular un lote
    path('api/lote/<int:lote_id>/anular/', views.anular_lote_ajax, name='anular_lote_ajax'),
    # URL para obtener los detalles de un lote
    path('api/lote/<int:lote_id>/detalles/', views.lote_detalle_ajax, name='lote_detalle_ajax'),
    # URL para exportar los detalles de un lote a PDF
    path('lote/<int:lote_id>/exportar-pdf/', views.exportar_lote_pdf, name='exportar_lote_pdf'),
]