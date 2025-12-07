# app_sabritas/admin.py - AÑADE ESTO
from django.contrib import admin
from .models import Clientes, Marcas, Categorias, Productos, Carrito, CarritoItem, Ventas, DetalleVenta

@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'usuario', 'email', 'telefono', 'fecha_registro']
    list_filter = ['fecha_registro']
    search_fields = ['nombre', 'apellido', 'email', 'usuario__username']
    
    # Si quieres mantener los campos de alergias y preferencias
    fieldsets = (
        ('Información Personal', {
            'fields': ('usuario', 'nombre', 'apellido', 'email', 'telefono')
        }),
        ('Información Adicional', {
            'fields': ('alergias', 'preferencias', 'fecha_registro')
        }),
    )

# Registra tus otros modelos...
admin.site.register(Marcas)
admin.site.register(Categorias)
admin.site.register(Productos)
admin.site.register(Carrito)
admin.site.register(CarritoItem)    
admin.site.register(Ventas)
admin.site.register(DetalleVenta)