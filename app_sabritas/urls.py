# app_sabritas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Vistas públicas
    path('', views.inicio, name='inicio'),
    path('registro/', views.registro, name='registro'),
    path('login/cliente/', views.cliente_login, name='cliente_login'),
    path('login/admin/', views.admin_login, name='admin_login'),
    path('logout/', views.custom_logout, name='logout'),
    path('marca/<int:marca_id>/', views.productos_por_marca, name='productos_marca'),
    
    # Carrito y compras
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_carrito, name='eliminar_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    
    
    # CRUD Marcas
    path('admin-app/marcas/', views.marcas_lista, name='marcas_lista'),
    path('admin-app/marcas/agregar/', views.marcas_agregar, name='marcas_agregar'),
    path('admin-app/marcas/editar/<int:id>/', views.marcas_editar, name='marcas_editar'),
    path('admin-app/marcas/eliminar/<int:id>/', views.marcas_eliminar, name='marcas_eliminar'),
    
    # CRUD Categorías
    path('admin-app/categorias/', views.categorias_lista, name='categorias_lista'),
    path('admin-app/categorias/agregar/', views.categorias_agregar, name='categorias_agregar'),
    path('admin-app/categorias/editar/<int:id>/', views.categorias_editar, name='categorias_editar'),
    path('admin-app/categorias/eliminar/<int:id>/', views.categorias_eliminar, name='categorias_eliminar'),
    
    # CRUD Productos
    path('admin-app/productos/', views.productos_lista, name='productos_lista'),
    path('admin-app/productos/agregar/', views.productos_agregar, name='productos_agregar'),
    path('admin-app/productos/editar/<int:id>/', views.productos_editar, name='productos_editar'),
    path('admin-app/productos/eliminar/<int:id>/', views.productos_eliminar, name='productos_eliminar'),
    
    # Clientes y ventas
    path('admin-app/clientes/', views.clientes_lista, name='clientes_lista'),
    path('admin-app/clientes/eliminar/<int:id>/', views.cliente_eliminar, name='cliente_eliminar'),
    path('admin-app/ventas/', views.ventas_lista, name='ventas_lista'),
    path('admin-app/ventas/<int:id>/', views.ventas_detalle, name='ventas_detalle'),
    path('admin-app/ventas/<int:id>/actualizar/', views.ventas_actualizar_estado, name='ventas_actualizar_estado'),

    path('productos/marca/<int:marca_id>/', views.productos_marca, name='productos_marca'),
    path('productos/marca/<int:marca_id>/categoria/<int:categoria_id>/', 
         views.productos_marca_categoria, 
         name='productos_marca_categoria'),
]