from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import GenerarCuotaForm
from .models import LoteGeneracion

@login_required
def generar_cuota_view(request):
    if request.method == 'POST':
        form = GenerarCuotaForm(request.POST)
        if form.is_valid():
            # Creamos el lote de generación pero no lo guardamos aún (commit=False)
            lote = LoteGeneracion(
                carrera=form.cleaned_data.get('carrera'),
                cohorte=form.cleaned_data.get('cohorte'),
                plan_pago=form.cleaned_data.get('plan_pago'),
                mes_generado=form.cleaned_data.get('mes'),
                año_generado=form.cleaned_data.get('año'),
                dia_vencimiento=form.cleaned_data.get('dia_vencimiento'),
                forzar_regeneracion=form.cleaned_data.get('forzar_regeneracion', False),
                usuario_generador=request.user,
            )
            lote.save() # Guardamos el lote en la base de datos

            messages.success(request, f"Se ha iniciado la generación del lote de cuotas. Podrá ver el estado en esta pantalla.")
            return redirect(reverse_lazy('reportes:lista_reportes'))
    else:
        form = GenerarCuotaForm()
    return render(request, 'cuotas/generar-cuota.html', {'form': form})

@login_required
def ajustes_manuales_view(request):
    return render(request, 'cuotas/ajustes-manuales.html')