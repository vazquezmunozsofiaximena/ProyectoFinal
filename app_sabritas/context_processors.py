# app_sabritas/context_processors.py
from .models import Carrito

def carrito_count(request):
    """Agregar el contador del carrito a todos los templates"""
    if request.user.is_authenticated:
        try:
            carrito = Carrito.objects.get(usuario=request.user, activo=True)
            count = carrito.total_items()
        except Carrito.DoesNotExist:
            count = 0
    else:
        count = 0
    
    return {'carrito_count': count}
# app_sabritas/context_processors.py
from .models import Marcas, Categorias

def menu_categorias(request):
    """Pasa las categorías organizadas por marca a todos los templates"""
    
    # Obtener todas las marcas principales
    marcas_principales = Marcas.objects.all()[:4]  # Sabritas, Doritos, Cheetos, Ruffles
    
    # Diccionario para organizar categorías por marca
    categorias_por_marca = {}
    
    for marca in marcas_principales:
        # Obtener categorías que tienen productos de esta marca
        categorias = Categorias.objects.filter(
            productos__marca=marca
        ).distinct()
        
        categorias_por_marca[f'categorias_marca_{marca.id}'] = categorias
    
    # También pasar las marcas
    categorias_por_marca['marcas_menu'] = marcas_principales
    
    return categorias_por_marca