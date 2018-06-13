from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Quatri)


@admin.register(Facultad)
class FacultadAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'last_updated', 'actions_facu')

    def actions_facu(self, obj):
        return format_html(
            '<a class="button" href="{}">Actualizar</a>&nbsp;'
            '<a class="button" href="{}">Cargar</a>',
            reverse(obj.name+'Init'),
            reverse(obj.name+'Assigs'),
        )
    actions_facu.short_description = "Acciones"


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_filter = ('facultad',)
    list_display = ('name', 'facultad', 'codigo')


@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_filter = ('carrera', 'cuatri')
    list_display = ('name', 'carrera', 'cuatri', 'loaded')


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'subgrupo')
