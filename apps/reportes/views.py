from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.cuotas.models import LoteGeneracion, Cuota # Importamos Cuota
from django.template.defaultfilters import date as _date, capfirst
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import json, datetime

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
    lotes = LoteGeneracion.objects.filter(activo=True).select_related('usuario_generador', 'plan_pago').prefetch_related('alumnos').all()
    
    data = []
    for lote in lotes:
        # Hacemos la vista más robusta por si un lote no tuviera plan de pago
        if lote.plan_pago:
            plan_nombre = lote.plan_pago.nombre
            monto_str = f"${lote.monto_total_estimado:,.2f}" if lote.monto_total_estimado is not None else "$0.00"
        else:
            plan_nombre = "N/A (Plan no encontrado)"
            monto_str = "$0.00"

        data.append({
            'id': lote.id,
            'fecha_creacion': _date(lote.fecha_generacion, "d/m/Y H:i"),
            'usuario': lote.usuario_generador.username,
            'plan_pago': plan_nombre,
            'estado': capfirst(lote.get_estado_display()), # Usamos get_..._display para obtener el texto legible
            'fecha_programacion': _date(lote.fecha_programacion, "d/m/Y H:i") if lote.fecha_programacion else "-",
            'monto_total': monto_str,
            'acciones': f"""
                <button class="btn btn-info btn-sm" onclick="verResumen({lote.id})">Ver</button>
                <button class="btn btn-danger btn-sm" onclick="prepararAnulacion({lote.id})">Borrar</button>
            """
        })
    
    return JsonResponse({'data': data})

@login_required
@require_POST
def anular_lote_ajax(request, lote_id):
    try:
        lote = LoteGeneracion.objects.get(id=lote_id)
        data = json.loads(request.body)
        motivo = data.get('motivo', '').strip()

        if not motivo:
            return JsonResponse({'status': 'error', 'message': 'El motivo de anulación es obligatorio.'}, status=400)

        lote.activo = False
        lote.save()
        # También podrías anular las cuotas asociadas si existen
        # Cuota.objects.filter(lote=lote).update(estado='ANULADA')
        return JsonResponse({'status': 'ok', 'message': 'Lote anulado correctamente.'})
    except LoteGeneracion.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El lote no existe.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def lote_detalle_ajax(request, lote_id):
    try:
        lote = LoteGeneracion.objects.select_related(
            'usuario_generador', 'plan_pago', 'plan_pago__carrera'
        ).get(id=lote_id)

        # Aquí asumimos que ya tienes el modelo Cuota y que se generaron
        # Simplificamos la consulta para hacerla más robusta.
        # Django hará joins adicionales, pero evitamos errores silenciosos.
        cuotas = Cuota.objects.filter(lote=lote).select_related('alumno').order_by('alumno__apellido', 'vencimiento')

        alumnos_data = []
        today = datetime.date.today()
        for cuota in cuotas:
            # Lógica para determinar el estado real de la cuota
            estado_real = cuota.get_estado_display()
            if cuota.estado == 'PENDIENTE' and cuota.vencimiento < today:
                estado_real = 'Vencida'

            alumnos_data.append({
                'legajo': cuota.alumno.legajo,
                'apellido': cuota.alumno.apellido,
                'nombre': cuota.alumno.nombre,
                'cohorte': cuota.alumno.cohorte,
                'carrera': cuota.alumno.carrera.nombre,
                'email': cuota.alumno.email,
                'plan_pago_alumno': cuota.alumno.plan_de_pago.nombre if cuota.alumno.plan_de_pago else 'N/A',
                'monto_cuota': f"${cuota.monto:,.2f}",
                'periodo': _date(cuota.vencimiento, "M-Y"), # Ej: Mar-2024
                'estado': estado_real,
                'vencimiento': _date(cuota.vencimiento, "d/m/Y"),
            })

        data = {
            'plan_nombre': lote.plan_pago.nombre,
            'carrera_nombre': lote.plan_pago.carrera.nombre,
            'carrera_modalidad': lote.plan_pago.carrera.get_modalidad_display(),
            'cantidad_cuotas': lote.plan_pago.cantidad_cuotas,
            'mora': f"{lote.plan_pago.mora}%",
            'valor_cuota': f"${lote.plan_pago.monto_mensual:,.2f}",
            'fecha_creacion': _date(lote.fecha_generacion, "d/m/Y H:i"),
            'creado_por': lote.usuario_generador.username,
            'estado_lote': lote.get_estado_display(),
            'monto_total_estimado': f"${lote.monto_total_estimado:,.2f}" if lote.monto_total_estimado is not None else "$0.00",
            'alumnos': alumnos_data,
        }
        return JsonResponse(data)
    except LoteGeneracion.DoesNotExist:
        return JsonResponse({'error': 'Lote no encontrado'}, status=404)

@login_required
def exportar_lote_pdf(request, lote_id):
    try:
        lote = LoteGeneracion.objects.select_related('usuario_generador', 'plan_pago', 'plan_pago__carrera').get(id=lote_id)
        cuotas = Cuota.objects.filter(lote=lote).select_related('alumno').order_by('alumno__apellido', 'vencimiento')
    except LoteGeneracion.DoesNotExist:
        return HttpResponse("Lote no encontrado.", status=404)

    # 1. Configurar la respuesta HTTP para que sea un PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="resumen_lote_{lote_id}.pdf"'

    # 2. Crear el documento PDF
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = []

    # 3. Añadir Título y detalles del lote
    story.append(Paragraph(f"Resumen del Lote de Cuotas #{lote.id}", styles['h1']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Plan de Pago:</b> {lote.plan_pago.nombre}", styles['Normal']))
    story.append(Paragraph(f"<b>Carrera:</b> {lote.plan_pago.carrera}", styles['Normal']))
    story.append(Paragraph(f"<b>Generado por:</b> {lote.usuario_generador.username} el {_date(lote.fecha_generacion, 'd/m/Y H:i')}", styles['Normal']))
    story.append(Spacer(1, 24))

    # 4. Preparar los datos para la tabla de cuotas
    table_data = [
        ['Legajo', 'Alumno', 'Período', 'Vencimiento', 'Monto', 'Estado']
    ]
    today = datetime.date.today()
    for cuota in cuotas:
        # Replicamos la misma lógica para el PDF
        estado_real = cuota.get_estado_display()
        if cuota.estado == 'PENDIENTE' and cuota.vencimiento < today:
            estado_real = 'Vencida'

        table_data.append([
            cuota.alumno.legajo,
            f"{cuota.alumno.apellido}, {cuota.alumno.nombre}",
            _date(cuota.vencimiento, "M-Y"),
            _date(cuota.vencimiento, "d/m/Y"),
            f"${cuota.monto:,.2f}",
            estado_real
        ])

    # 5. Crear y estilizar la tabla
    cuotas_table = Table(table_data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    cuotas_table.setStyle(style)

    story.append(cuotas_table)

    # 6. Construir el PDF
    doc.build(story)

    return response