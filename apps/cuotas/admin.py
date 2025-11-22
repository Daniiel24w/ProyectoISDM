from django.contrib import admin
from .models import Carrera, PlanDePago, LoteGeneracion, Alumno, Cuota


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'modalidad')
    search_fields = ('nombre',)

@admin.register(PlanDePago)
class PlanDePagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'anio', 'carrera', 'monto_mensual', 'cantidad_cuotas', 'mora')
    list_filter = ('anio', 'carrera')
    search_fields = ('nombre', 'carrera__nombre')

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('legajo', 'apellido', 'nombre', 'carrera', 'cohorte', 'plan_de_pago')
    list_filter = ('carrera', 'cohorte', 'plan_de_pago')
    search_fields = ('legajo', 'apellido', 'nombre', 'dni')
    # El campo 'legajo' es la PK, por lo que es de solo lectura por defecto en la edición.

@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ('id', 'alumno', 'lote_id', 'monto', 'vencimiento', 'estado')
    list_filter = ('estado', 'vencimiento', 'lote__plan_pago')
    search_fields = ('alumno__legajo', 'alumno__apellido', 'alumno__nombre', 'lote__id')
    list_per_page = 25

admin.site.register(LoteGeneracion)