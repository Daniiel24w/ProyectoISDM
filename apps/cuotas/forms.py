from django import forms
import datetime


class GenerarCuotaForm(forms.Form):
    # --- Filtro de Generación ---
    plan_pago = forms.ChoiceField(
        label="Plan de Pago",
        choices=[('', 'Seleccionar Plan de Pago')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    alumnos_seleccionados = forms.CharField(widget=forms.HiddenInput(), required=False)

    forzar_regeneracion = forms.BooleanField(
        label="Forzar regeneración de cuotas existentes",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    # --- Vencimiento ---
    DIAS_VENCIMIENTO = [(i, f"El día {i} del mes") for i in range(1, 31)]
    dia_vencimiento = forms.ChoiceField(
        label="Día de Vencimiento",
        choices=[('', 'Seleccionar día de vencimiento')] + DIAS_VENCIMIENTO,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    manejo_dias_no_habiles = forms.CharField(
        label="Manejo de días no hábiles",
        initial="Mover hasta el siguiente día hábil",
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True})
    )

    # --- Mora ---
    frecuencia_mora = forms.CharField(
        label="Frecuencia de Mora",
        initial="Por única vez",
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True})
    )

    def __init__(self, *args, **kwargs):
        planes_pago_queryset = kwargs.pop('planes_pago', None) # Extraemos el queryset de los kwargs
        super().__init__(*args, **kwargs)

        if planes_pago_queryset:
            self.fields['plan_pago'].choices = [('', 'Seleccionar Plan de Pago')] + [(p.id, str(p)) for p in planes_pago_queryset]