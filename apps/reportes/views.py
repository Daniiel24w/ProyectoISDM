from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.cuotas.models import LoteGeneracion
from django.template.defaultfilters import date as _date, capfirst

@login_required
def lista_reportes_view(request):
    """
    Renderiza la página principal de supervisión de lotes.
    La tabla se cargará vía AJAX con DataTables.
    """
    return render(request, 'reportes/reportes.html')

@login_required
def lotes_data_ajax(request):
    """
    Provee los datos de los lotes en formato JSON para DataTables.
    """
    lotes = LoteGeneracion.objects.select_related('usuario_generador', 'carrera', 'plan_pago').all()
    
    data = []
    for lote in lotes:
        # Construir la descripción de los filtros de forma legible
        filtros = []
        if lote.carrera:
            filtros.append(f"Carrera: {lote.carrera.nombre}")
        if lote.cohorte:
            filtros.append(f"Cohorte: {lote.cohorte}")
        if lote.plan_pago:
            filtros.append(f"Plan: {lote.plan_pago.nombre}")
        filtros_str = ", ".join(filtros) if filtros else "Todos"

        data.append({
            'id': lote.id,
            'fecha_ejecucion': _date(lote.fecha_generacion, "d/m/Y H:i"),
            'usuario': lote.usuario_generador.username,
            'filtros_aplicados': filtros_str,
            'estado': capfirst(lote.get_estado_display()), # Usamos get_..._display para obtener el texto legible
        })
    
    return JsonResponse({'data': data})