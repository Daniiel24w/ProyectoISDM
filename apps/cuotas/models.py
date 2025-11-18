from django.db import models
from django.contrib.auth.models import User

class Carrera(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Carrera")

    class Meta:
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"

    def __str__(self):
        return self.nombre

class PlanDePago(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Plan")

    class Meta:
        verbose_name = "Plan de Pago"
        verbose_name_plural = "Planes de Pago"

    def __str__(self):
        return self.nombre

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
    carrera = models.ForeignKey(Carrera, on_delete=models.SET_NULL, null=True, blank=True)
    cohorte = models.IntegerField(null=True, blank=True)
    plan_pago = models.ForeignKey(PlanDePago, on_delete=models.SET_NULL, null=True, blank=True)
    mes_generado = models.IntegerField()
    año_generado = models.IntegerField()

    # Parámetros de generación
    dia_vencimiento = models.IntegerField()
    forzar_regeneracion = models.BooleanField(default=False)

    # Datos del proceso
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    usuario_generador = models.ForeignKey(User, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    
    # (Opcional) Podríamos añadir los parámetros de mora aquí también si es necesario

    class Meta:
        verbose_name = "Lote de Generación"
        verbose_name_plural = "Lotes de Generación"
        ordering = ['-fecha_generacion']

    def __str__(self):
        return f"Lote generado por {self.usuario_generador.username} el {self.fecha_generacion.strftime('%d/%m/%Y %H:%M')}"