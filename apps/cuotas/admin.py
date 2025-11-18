from django.contrib import admin
from .models import Carrera, PlanDePago, LoteGeneracion

# Register your models here.
admin.site.register(Carrera)
admin.site.register(PlanDePago)
admin.site.register(LoteGeneracion)