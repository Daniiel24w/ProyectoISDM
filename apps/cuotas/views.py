from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.template.defaultfilters import date as _date
from dateutil.relativedelta import relativedelta
from .forms import GenerarCuotaForm
from .models import LoteGeneracion, Carrera, PlanDePago, Alumno, Cuota
from django.db.models import Q
import datetime, json

@login_required
def generar_cuota_view(request):
    # Obtenemos los datos para poblar los selectores del formulario
    planes_pago = PlanDePago.objects.all()

    if request.method == 'POST':
        # Al instanciar el form en POST, también le pasamos los querysets
        form = GenerarCuotaForm(request.POST, planes_pago=planes_pago)
        if form.is_valid():
            # --- 1. OBTENER ALUMNOS Y DATOS DEL PLAN ---
            legajos_seleccionados_json = form.cleaned_data.get('alumnos_seleccionados')
            plan_pago_id = form.cleaned_data.get('plan_pago')
            
            try:
                plan_pago_obj = PlanDePago.objects.get(id=plan_pago_id)
                legajos_seleccionados = json.loads(legajos_seleccionados_json) if legajos_seleccionados_json else []
                alumnos_a_procesar = Alumno.objects.filter(legajo__in=legajos_seleccionados)
            except (PlanDePago.DoesNotExist, json.JSONDecodeError):
                messages.error(request, "Hubo un error al procesar los datos. Intente de nuevo.")
                return redirect('cuotas:generar_cuota')

            if not alumnos_a_procesar.exists():
                messages.warning(request, "No se seleccionó ningún alumno para procesar.")
                return redirect('cuotas:generar_cuota')

            # --- 2. CALCULAR MONTO TOTAL CORRECTO ---
            monto_total_estimado_real = plan_pago_obj.monto_mensual * plan_pago_obj.cantidad_cuotas * alumnos_a_procesar.count()

            # --- 3. CREAR Y GUARDAR EL LOTE ---
            lote = LoteGeneracion(
                carrera=plan_pago_obj.carrera,
                plan_pago=plan_pago_obj,
                mes_generado=datetime.date.today().month,
                anio_generado=plan_pago_obj.anio,
                dia_vencimiento=int(form.cleaned_data.get('dia_vencimiento')), # Convertimos a entero
                monto_total_estimado=monto_total_estimado_real, # Usamos el monto correcto
                forzar_regeneracion=form.cleaned_data.get('forzar_regeneracion', False),
                usuario_generador=request.user,
                tipo_recargo='porcentaje',
                valor_mora=plan_pago_obj.mora,
                frecuencia_mora=form.cleaned_data.get('frecuencia_mora'),
            )

            # Diferenciar si se generó o se programó
            if 'generar' in request.POST:
                lote.estado = 'COMPLETADO'
                messages.success(request, f"Lote generado para {alumnos_a_procesar.count()} alumnos. Monto total estimado: ${monto_total_estimado_real:,.2f}.")
            elif 'programar' in request.POST:
                fecha_str = request.POST.get('fecha_programacion')
                hora_str = request.POST.get('hora_programacion')
                if fecha_str and hora_str:
                    fecha_hora_programacion = datetime.datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
                    if fecha_hora_programacion < datetime.datetime.now():
                        messages.error(request, "La fecha de programación no puede ser en el pasado.")
                        return redirect('cuotas:generar_cuota')
                    fecha_hora_programacion = datetime.datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
                    lote.fecha_programacion = fecha_hora_programacion
                    lote.estado = 'PENDIENTE'
                    messages.success(request, f"Lote programado para el {fecha_hora_programacion.strftime('%d/%m/%Y a las %H:%M hs')}.")

            lote.save()
            lote.alumnos.set(alumnos_a_procesar) # Asociamos los alumnos al lote

            # --- 4. CREAR LAS CUOTAS INDIVIDUALES ---
            if lote.estado == 'COMPLETADO':
                cuotas_a_crear = []
                for alumno in alumnos_a_procesar:
                    for i in range(plan_pago_obj.cantidad_cuotas):
                        fecha_base = datetime.date(lote.anio_generado, lote.mes_generado, 1)
                        fecha_vencimiento_calculada = fecha_base + relativedelta(months=i)
                        fecha_vencimiento_final = fecha_vencimiento_calculada.replace(day=lote.dia_vencimiento)

                        cuotas_a_crear.append(
                            Cuota(
                                alumno=alumno,
                                lote=lote,
                                monto=plan_pago_obj.monto_mensual,
                                vencimiento=fecha_vencimiento_final,
                                estado='PENDIENTE'
                            )
                        )
                if cuotas_a_crear:
                    # Usamos bulk_create para una inserción masiva y eficiente
                    Cuota.objects.bulk_create(cuotas_a_crear)
                    messages.info(request, f"Se crearon {len(cuotas_a_crear)} cuotas individuales.")
                else:
                    messages.warning(request, "No se crearon cuotas individuales. Verifique la lógica de generación.")

            return redirect(reverse_lazy('reportes:lista_reportes'))
    else:
        # Al instanciar el form en GET, le pasamos los querysets para que se muestren las opciones
        form = GenerarCuotaForm(planes_pago=planes_pago)

    return render(request, 'cuotas/generar-cuota.html', {'form': form})

@login_required
def ajustes_manuales_view(request):
    return render(request, 'cuotas/ajustes-manuales.html')


@login_required
def get_alumnos_por_plan(request):
    plan_id = request.GET.get('plan_id')
    if not plan_id:
        return JsonResponse({'error': 'ID de plan no proporcionado'}, status=400)

    try:
        plan = PlanDePago.objects.select_related('carrera').get(id=plan_id)
        alumnos = Alumno.objects.filter(plan_de_pago=plan).order_by('-cohorte', 'apellido', 'nombre')
        
        alumnos_data = [{
            'legajo': a.legajo,
            'nombre_completo': f"{a.apellido.upper()}, {a.nombre.title()}",
            'cohorte': a.cohorte
        } for a in alumnos]

        return JsonResponse({
            'carrera': {
                'id': plan.carrera.id, 
                'nombre': plan.carrera.nombre,
                'modalidad': plan.carrera.get_modalidad_display() # Enviamos la modalidad
            },
            'plan_anio': plan.anio, # Enviamos el año del plan
            'plan_mora': plan.mora, # Enviamos el valor de la mora
            'alumnos': alumnos_data,
        })
    except PlanDePago.DoesNotExist:
        return JsonResponse({'error': 'Plan de pago no encontrado'}, status=404)

@login_required
def buscar_cuotas_alumno_api(request):
    termino_busqueda = request.GET.get('termino', '').strip()
    if not termino_busqueda:
        return JsonResponse({'error': 'Debe ingresar un término de búsqueda.'}, status=400)

    try:
        # Buscamos por legajo o DNI
        alumno = Alumno.objects.select_related('carrera', 'plan_de_pago').get(
            Q(legajo__iexact=termino_busqueda) | Q(dni__iexact=termino_busqueda)
        )
    except Alumno.DoesNotExist:
        return JsonResponse({'error': 'Alumno no encontrado.'}, status=404)

    cuotas = Cuota.objects.filter(alumno=alumno).select_related('lote__plan_pago').order_by('-vencimiento')

    alumno_data = {
        'legajo': alumno.legajo,
        'nombre_completo': f"{alumno.apellido}, {alumno.nombre}",
        'dni': alumno.dni,
        'email': alumno.email,
        'carrera': alumno.carrera.nombre,
        'plan_actual': alumno.plan_de_pago.nombre if alumno.plan_de_pago else "No asignado"
    }

    cuotas_data = [{
        'id': c.id,
        'plan_pago': c.lote.plan_pago.nombre,
        'monto_original': f"${c.monto:,.2f}",
        'monto_final': f"${c.monto_ajustado:,.2f}" if c.monto_ajustado is not None else f"${c.monto:,.2f}",
        'vencimiento_original': _date(c.vencimiento, "d/m/Y"),
        'vencimiento_final': _date(c.vencimiento_ajustado, "d/m/Y") if c.vencimiento_ajustado else "-",
        'estado': c.get_estado_display(),
        'periodo': _date(c.vencimiento, "M-Y"),
        'es_ajustable': c.estado in ['PENDIENTE', 'VENCIDA']
    } for c in cuotas]

    return JsonResponse({'alumno': alumno_data, 'cuotas': cuotas_data})

@login_required
@require_POST
def ajustar_cuota_api(request, cuota_id):
    try:
        cuota = Cuota.objects.get(id=cuota_id)
        data = json.loads(request.body)

        nuevo_vencimiento_str = data.get('vencimiento')
        nuevo_monto_str = data.get('monto')
        motivo = data.get('motivo')

        if not motivo:
            return JsonResponse({'error': 'El motivo es obligatorio.'}, status=400)

        if nuevo_vencimiento_str:
            cuota.vencimiento_ajustado = nuevo_vencimiento_str
        if nuevo_monto_str:
            cuota.monto_ajustado = nuevo_monto_str.replace('$', '').replace('.', '').replace(',', '.')
        
        cuota.motivo_ajuste = motivo
        cuota.save()
        return JsonResponse({'status': 'ok', 'message': 'Cuota ajustada correctamente.'})
    except Cuota.DoesNotExist:
        return JsonResponse({'error': 'Cuota no encontrada.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)