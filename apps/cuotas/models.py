from django.db import models
from django.contrib.auth.models import User


class Carrera(models.Model):
    MODALIDAD_CHOICES = [
        ('PRESENCIAL', 'Presencial'),
        ('VIRTUAL', 'Virtual'),
    ]
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Carrera")
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES, default='PRESENCIAL', verbose_name="Modalidad")

    class Meta:
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"
        # Asegura que la combinación de nombre y modalidad sea única.
        unique_together = ('nombre', 'modalidad')
        ordering = ['nombre', 'modalidad']

    def __str__(self):
        return f"{self.nombre} ({self.get_modalidad_display()})"


class PlanDePago(models.Model):
    """Representa una plantilla o tipo de plan de pago, no una cuota individual."""
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Plan")
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, verbose_name="Carrera Asociada")
    anio = models.IntegerField(verbose_name="Año del Plan", default=2023)
    monto_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Monto Mensual Base")
    cantidad_cuotas = models.IntegerField(default=10, verbose_name="Cantidad de Cuotas Anuales")
    mora = models.PositiveIntegerField(default=0, verbose_name="Mora (%)", help_text="Porcentaje de recargo por mora. Ej: 10 para un 10%")

    class Meta:
        verbose_name = "Plan de Pago"
        verbose_name_plural = "Planes de Pago"
        # Permite reutilizar un nombre de plan para la misma carrera pero en diferentes años.
        unique_together = ('nombre', 'carrera', 'anio')
        ordering = ['-anio', 'carrera', 'nombre']

    def __str__(self):
        if self.carrera:
            return f"{self.nombre} - {self.anio} ({self.carrera.nombre})"
        # Este caso ya no debería ocurrir al ser la carrera obligatoria
        return f"{self.nombre} - {self.anio} (Sin carrera asignada)"


class Alumno(models.Model):
    """Modela la información de un alumno."""
    legajo = models.CharField(max_length=20, primary_key=True, verbose_name="Legajo")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, verbose_name="Apellido")
    dni = models.CharField(max_length=10, unique=True, verbose_name="DNI")
    email = models.EmailField(unique=True, verbose_name="Email")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    cohorte = models.IntegerField(verbose_name="Cohorte de Ingreso")
    carrera = models.ForeignKey(Carrera, on_delete=models.PROTECT, verbose_name="Carrera")
    plan_de_pago = models.ForeignKey(PlanDePago, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Plan de Pago Asignado")

    class Meta:
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.legajo})"


class LoteGeneracion(models.Model):
    """
    Registra cada proceso de generación de cuotas para trazabilidad.
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PROCESANDO', 'Procesando'),
        ('COMPLETADO', 'Completado'),
        ('ERROR', 'Error'),
    ]

    # Filtros aplicados
    carrera = models.ForeignKey(Carrera, on_delete=models.PROTECT, help_text="Generar cuotas para alumnos de esta carrera.")
    plan_pago = models.ForeignKey(PlanDePago, on_delete=models.PROTECT, help_text="Generar cuotas solo para alumnos con este plan.")
    mes_generado = models.IntegerField()
    anio_generado = models.IntegerField()
    alumnos = models.ManyToManyField(Alumno, related_name="lotes_generacion", blank=True)

    # Parámetros de generación
    monto_total_estimado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Monto mensual del plan por la cantidad de cuotas.")
    dia_vencimiento = models.IntegerField()
    forzar_regeneracion = models.BooleanField(default=False)
    
    # Parámetros de mora
    TIPO_RECARGO_CHOICES = [('fijo', 'Monto Fijo'), ('porcentaje', 'Porcentaje')]
    tipo_recargo = models.CharField(max_length=10, choices=TIPO_RECARGO_CHOICES, default='fijo')
    valor_mora = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frecuencia_mora = models.CharField(max_length=50, default='Por única vez')

    # Datos del proceso
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_programacion = models.DateTimeField(null=True, blank=True, help_text="Si se programa, esta es la fecha y hora de ejecución.")
    usuario_generador = models.ForeignKey(User, on_delete=models.PROTECT)
    activo = models.BooleanField(default=True, help_text="Indica si el lote está activo o fue anulado.")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')

    class Meta:
        verbose_name = "Lote de Generación"
        verbose_name_plural = "Lotes de Generación"
        ordering = ['-fecha_generacion']

    def __str__(self):
        return f"Lote generado por {self.usuario_generador.username} el {self.fecha_generacion.strftime('%d/%m/%Y %H:%M')}"


class Cuota(models.Model):
    """Representa una cuota individual de un alumno."""
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADA', 'Pagada'),
        ('VENCIDA', 'Vencida'),
        ('ANULADA', 'Anulada'),
    ]

    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='cuotas')
    lote = models.ForeignKey(LoteGeneracion, on_delete=models.CASCADE, related_name='cuotas')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    monto_ajustado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Nuevo monto si se aplica un ajuste manual.")
    vencimiento = models.DateField()
    vencimiento_ajustado = models.DateField(null=True, blank=True, help_text="Nueva fecha de vencimiento si se aplica un ajuste.")
    fecha_pago = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    motivo_ajuste = models.TextField(blank=True, null=True, help_text="Razón del ajuste manual.")

    class Meta:
        verbose_name = "Cuota"
        verbose_name_plural = "Cuotas"
        ordering = ['-vencimiento', 'alumno']
        unique_together = ('alumno', 'vencimiento') # Un alumno solo puede tener una cuota por fecha de vencimiento

    def __str__(self):
        return f"Cuota de {self.alumno} - Vence: {self.vencimiento}"