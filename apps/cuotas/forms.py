from django import forms
from .models import Carrera, PlanDePago
import datetime

class GenerarCuotaForm(forms.Form):
    # --- Filtros de Generación ---
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all(),
        label="Carrera",
        required=False,
        empty_label="Todas",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Años hardcodeados: 2015 a 2035
    YEAR_CHOICES = [(year, str(year)) for year in range(2015, 2036)]
    cohorte = forms.ChoiceField(
        choices=[('', 'Todas')] + YEAR_CHOICES,
        label="Cohorte",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    plan_pago = forms.ModelChoiceField(
        queryset=PlanDePago.objects.all(),
        label="Plan de pago",
        required=False,
        empty_label="Todos",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Meses hardcodeados
    MONTH_CHOICES = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]
    mes = forms.ChoiceField(
        choices=MONTH_CHOICES,
        label="Mes",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    año = forms.ChoiceField(
        choices=YEAR_CHOICES,
        label="Año",
        initial=datetime.date.today().year,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    forzar_regeneracion = forms.BooleanField(
        label="Forzar Regeneración",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    # --- Vencimiento ---
    dia_vencimiento = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 32)],
        label="Día de vencimiento",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    MANEJO_DIAS_NO_HABILES_CHOICES = [
        ('SIGUIENTE', 'Mover al siguiente día hábil'),
        ('ANTERIOR', 'Mover al día hábil anterior'),
        ('MANTENER', 'Mantener fecha exacta'),
    ]
    manejo_dias_no_habiles = forms.ChoiceField(
        choices=MANEJO_DIAS_NO_HABILES_CHOICES,
        label="Días no hábiles",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # --- Mora ---
    TIPO_RECARGO_CHOICES = [
        ('FIJO', 'Fijo'),
        ('PORCENTAJE', 'Porcentaje'),
    ]
    tipo_recargo = forms.ChoiceField(
        choices=TIPO_RECARGO_CHOICES,
        label="Tipo de recargo",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    valor_mora = forms.DecimalField(
        label="Valor",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'})
    )

    FRECUENCIA_MORA_CHOICES = [
        ('UNICA', 'Por única vez (al vencimiento)'),
        ('MENSUAL', 'Por mes de atraso'),
    ]
    frecuencia_mora = forms.ChoiceField(
        choices=FRECUENCIA_MORA_CHOICES,
        label="Frecuencia",
        widget=forms.Select(attrs={'class': 'form-select'})
    )