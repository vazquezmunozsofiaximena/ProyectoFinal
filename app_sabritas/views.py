# app_sabritas/views.py
from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import *
from .forms import *

# Decorador para verificar si es staff
def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)

# views.py
def inicio(request):
    from app_sabritas.models import Marcas, Categorias, Productos
    
    # Obtener marcas principales
    marcas_principales = Marcas.objects.all()[:4]
    
    # Obtener productos destacados
    productos_destacados = Productos.objects.filter(stock__gt=0)[:8]
    
    # Obtener categorías para cada marca
    sabritas_categorias = Categorias.objects.filter(productos__marca_id=1).distinct()
    doritos_categorias = Categorias.objects.filter(productos__marca_id=2).distinct()
    cheetos_categorias = Categorias.objects.filter(productos__marca_id=3).distinct()
    ruffles_categorias = Categorias.objects.filter(productos__marca_id=4).distinct()
    
    return render(request, 'inicio.html', {
        'marcas': marcas_principales,
        'productos_destacados': productos_destacados,
        'sabritas_categorias': sabritas_categorias,
        'doritos_categorias': doritos_categorias,
        'cheetos_categorias': cheetos_categorias,
        'ruffles_categorias': ruffles_categorias,
    })
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Autenticar automáticamente
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, '¡Registro exitoso! Bienvenido a Sabritas.')
                return redirect('inicio')  # Cambia 'inicio' por tu página principal
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = RegistroForm()
    
    return render(request, 'registro.html', {'form': form})
    
    return render(request, 'registro.html', {'form': form})
def iniciar_sesion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido/a {user.username}!')
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'login.html')

def custom_logout(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('inicio')

def productos_por_marca(request, marca_id):
    marca = get_object_or_404(Marcas, id_marca=marca_id)
    categorias = Categorias.objects.filter(marca=marca)
    productos = Productos.objects.filter(marca=marca, stock__gt=0)
    
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    context = {
        'marca': marca,
        'categorias': categorias,
        'productos': productos,
        'categoria_seleccionada': categoria_id,
    }
    return render(request, 'productos_marca.html', context)

# VISTAS DE CARRITO
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app_sabritas.models import Carrito, CarritoItem, Productos

@login_required
def carrito(request):
    """Ver el carrito del usuario"""
    try:
        carrito = Carrito.objects.get(usuario=request.user, activo=True)
    except Carrito.DoesNotExist:
        # Si no existe carrito activo, crear uno nuevo
        carrito = Carrito.objects.create(usuario=request.user)
    
    items = carrito.items.all()
    
    # Calcular totales
    subtotal = carrito.subtotal_carrito()
    iva = carrito.calcular_iva()
    total = carrito.total_con_iva()
    items_count = carrito.total_items()
    
    return render(request, 'carrito.html', {
        'carrito': carrito,
        'items': items,
        'subtotal': subtotal,
        'iva': iva,
        'total': total,
        'items_count': items_count
    })

@login_required
def agregar_carrito(request, producto_id):
    """Agregar producto al carrito"""
    producto = get_object_or_404(Productos, id_producto=producto_id)
    
    # Verificar stock
    if producto.stock <= 0:
        messages.error(request, f'Lo sentimos, {producto.nombre} está agotado.')
        return redirect('inicio')
    
    # Obtener o crear carrito
    carrito, created = Carrito.objects.get_or_create(
        usuario=request.user,
        activo=True
    )
    
    # Verificar si el producto ya está en el carrito
    item, item_created = CarritoItem.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        defaults={'cantidad': 1}
    )
    
    if not item_created:
        # Si ya existe, aumentar cantidad
        item.cantidad += 1
        item.save()
        messages.success(request, f'Se agregó otra unidad de {producto.nombre}')
    else:
        messages.success(request, f'{producto.nombre} agregado al carrito!')
    
    return redirect('carrito')

@login_required
def actualizar_carrito(request, item_id):
    """Actualizar cantidad de un item del carrito"""
    item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
    
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        
        # Validar cantidad
        if cantidad < 1:
            item.delete()
            messages.info(request, 'Producto eliminado del carrito')
        elif cantidad > item.producto.stock:
            messages.error(request, f'No hay suficiente stock. Disponible: {item.producto.stock}')
        else:
            item.cantidad = cantidad
            item.save()
            messages.success(request, 'Cantidad actualizada')
    
    return redirect('carrito')

@login_required
def eliminar_carrito(request, item_id):
    """Eliminar item del carrito"""
    item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
    producto_nombre = item.producto.nombre
    item.delete()
    
    messages.success(request, f'{producto_nombre} eliminado del carrito')
    return redirect('carrito')

@login_required
def vaciar_carrito(request):
    """Vaciar todo el carrito"""
    carrito = get_object_or_404(Carrito, usuario=request.user, activo=True)
    items_count = carrito.items.count()
    carrito.items.all().delete()
    
    messages.success(request, f'Carrito vaciado. Se eliminaron {items_count} productos')
    return redirect('carrito')

@login_required
# views.py - vista checkout FINAL
@login_required
def checkout(request):
    """Vista para procesar el checkout/finalizar compra"""
    try:
        carrito_obj = Carrito.objects.get(usuario=request.user, activo=True)
        items = carrito_obj.items.all()
        
        if not items.exists():
            messages.error(request, 'No tienes items en el carrito')
            return redirect('carrito')
            
    except Carrito.DoesNotExist:
        messages.error(request, 'No tienes items en el carrito')
        return redirect('carrito')
    
    # Calcular totales
    subtotal = carrito_obj.subtotal_carrito()
    iva_monto = carrito_obj.calcular_iva()
    total_con_iva = carrito_obj.total_con_iva()
    
    # Verificar stock
    items_sin_stock = []
    for item in items:
        if item.cantidad > item.producto.stock:
            items_sin_stock.append(f"{item.producto.nombre} (Stock: {item.producto.stock})")
    
    if items_sin_stock:
        messages.error(request, f'Stock insuficiente: {", ".join(items_sin_stock)}')
        return redirect('carrito')
    
    if request.method == 'POST':
        try:
            # Crear venta - IMPORTANTE: usar id_venta y estado
            venta = Ventas.objects.create(
                cliente=request.user,
                subtotal=subtotal,
                iva=iva_monto,
                total=total_con_iva,
                direccion_envio=request.POST.get('direccion', ''),
                metodo_pago=request.POST.get('metodo_pago', 'Tarjeta de crédito'),
                estado='confirmado'  # AÑADIR ESTADO
            )
            
            # Reducir stock
            for item in items:
                producto = item.producto
                producto.stock -= item.cantidad
                producto.save()
            
            # Desactivar carrito y crear uno nuevo
            carrito_obj.activo = False
            carrito_obj.save()
            nuevo_carrito = Carrito.objects.create(usuario=request.user)
            
            # Redirigir a confirmacion_pedido
            return render(request, 'confirmacion_pedido.html', {
                'venta': venta,
                'venta_id': venta.id_venta,  # ⭐⭐ USAR id_venta, NO id ⭐⭐
                'items': items,
                'total': total_con_iva,
                'nuevo_carrito': nuevo_carrito,
            })
            
        except Exception as e:
            messages.error(request, f'Error al procesar la compra: {str(e)}')
            return redirect('carrito')
    
    # Si es GET, mostrar formulario
    context = {
        'carrito': carrito_obj,
        'items': items,
        'subtotal': subtotal,
        'iva': iva_monto,
        'total': total_con_iva,
        'items_count': carrito_obj.total_items(),
    }
    
    return render(request, 'checkout.html', context)
@login_required
def mis_pedidos(request):
    try:
        cliente = Clientes.objects.get(usuario=request.user)
        ventas = Ventas.objects.filter(cliente=request.user).order_by('-fecha_venta')
    except Clientes.DoesNotExist:
        ventas = []
    
    return render(request, 'mis_pedidos.html', {'ventas': ventas})

# VISTAS DE ADMINISTRACIÓN
# CRUD MARCAS
@staff_required
def marcas_lista(request):
    marcas = Marcas.objects.all()
    return render(request, 'admin-app/marcas/lista.html', {'marcas': marcas})

@staff_required
def marcas_agregar(request):
    if request.method == 'POST':
        form = MarcaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca agregada correctamente')
            return redirect('marcas_lista')
    else:
        form = MarcaForm()
    
    return render(request, 'admin-app/marcas/agregar.html', {'form': form})

@staff_required
def marcas_editar(request, id):
    marca = get_object_or_404(Marcas, id=id)
    
    if request.method == 'POST':
        form = MarcaForm(request.POST, request.FILES, instance=marca)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca actualizada correctamente')
            return redirect('marcas_lista')
    else:
        form = MarcaForm(instance=marca)
    
    return render(request, 'admin-app/marcas/editar.html', {'form': form, 'marca': marca})

@staff_required
def marcas_eliminar(request, id):
    marca = get_object_or_404(Marcas, id=id)
    
    if request.method == 'POST':
        marca.delete()
        messages.success(request, 'Marca eliminada correctamente')
        return redirect('marcas_lista')
    
    return render(request, 'admin-app/marcas/eliminar.html', {'marca': marca})

# CRUD CATEGORÍAS
@staff_required
def categorias_lista(request):
    categorias = Categorias.objects.all()
    return render(request, 'admin-app/categorias/lista.html', {'categorias': categorias})

@staff_required
def categorias_agregar(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría agregada correctamente')
            return redirect('categorias_lista')
    else:
        form = CategoriaForm()
    
    return render(request, 'admin-app/categorias/agregar.html', {'form': form})

@staff_required
def categorias_editar(request, id):
    categoria = get_object_or_404(Categorias, id=id)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada correctamente')
            return redirect('categorias_lista')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'admin-app/categorias/editar.html', {'form': form, 'categoria': categoria})

@staff_required
def categorias_eliminar(request, id):
    categoria = get_object_or_404(Categorias, id=id)
    
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada correctamente')
        return redirect('categorias_lista')
    
    return render(request, 'admin-app/categorias/eliminar.html', {'categoria': categoria})

# CRUD PRODUCTOS
@staff_required
def productos_lista(request):
    marcas = Marcas.objects.all()
    categorias = Categorias.objects.all()
    productos = Productos.objects.select_related('marca', 'categoria').all()
    return render(request, 'admin-app/productos/lista.html', {'marcas': marcas, 'categorias': categorias, 'productos': productos})

@staff_required
def productos_agregar(request):
    # OBTENER DATOS PARA EL FORMULARIO
    marcas = Marcas.objects.all()  # Esto debe existir
    categorias = Categorias.objects.all()  # Esto debe existir
    
    # Si no hay marcas o categorías, mostrar mensaje
    if not marcas.exists():
        messages.warning(request, 'Primero debes crear al menos una marca.')
        return redirect('marcas_agregar')
    
    if not categorias.exists():
        messages.warning(request, 'Primero debes crear al menos una categoría.')
        return redirect('categorias_agregar')
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto agregado correctamente')
            return redirect('productos_lista')
    # GET: Mostrar formulario CON las marcas y categorías
    return render(request, 'admin-app/productos/agregar.html', {
        'marcas': marcas,
        'categorias': categorias
    })

@staff_required
def productos_editar(request, id):
    producto = get_object_or_404(Productos, id_producto=id)
    marcas = Marcas.objects.all()
    categorias = Categorias.objects.all()
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente')
            return redirect('productos_lista')
        else:
            # FORZAR a mostrar los errores
            print("=" * 80)
            print("🔥🔥🔥 ERRORES DEL FORMULARIO 🔥🔥🔥")
            print(f"Formulario válido: {form.is_valid()}")
            print(f"Número de errores: {len(form.errors)}")
            
            # Mostrar TODOS los errores
            for field_name, errors in form.errors.items():
                print(f"\nCampo: '{field_name}'")
                for error in errors:
                    print(f"  ❌ Error: {error}")
            
            # Mostrar los datos que se enviaron
            print("\n📦 DATOS ENVIADOS:")
            for key, value in request.POST.items():
                print(f"  {key}: {value}")
            
            print("=" * 80)
            
            # Pasar los errores como mensaje
            error_mensaje = "Errores: "
            for field, errors in form.errors.items():
                for error in errors:
                    error_mensaje += f"{field}: {error}. "
            
            messages.error(request, error_mensaje[:200])  # Limitar longitud
    
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'admin-app/productos/editar.html', {
        'form': form,
        'producto': producto,
        'marcas': marcas,
        'categorias': categorias
    })
@staff_required
def productos_eliminar(request, id):
    producto = get_object_or_404(Productos, id_producto=id)
    
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado correctamente')
        return redirect('productos_lista')
    
    return render(request, 'admin-app/productos/eliminar.html', {'producto': producto})

# CRUD CLIENTES
@staff_required
def clientes_lista(request):
    clientes = Clientes.objects.all()
    return render(request, 'admin-app/clientes/lista.html', {'clientes': clientes})

@staff_required
def cliente_eliminar(request, id):
    usuario = get_object_or_404(Clientes, id_clientes=id)
    
    if request.method == 'POST':
        usuario = usuario.usuario
        email = usuario.email
        
        # Eliminar el usuario
        usuario.delete()
        
        messages.success(request, f'✅ Cliente {usuario} eliminado correctamente.')
        return redirect('clientes_lista')
    
    # Si es GET, mostrar confirmación
    context = {
        'usuario': usuario,
    }
    
    return render(request, 'admin-app/clientes/eliminar.html', context)

# VISTAS DE VENTAS
@staff_required
def ventas_lista(request):
    ventas = Ventas.objects.select_related('cliente').all().order_by('-fecha_venta')
    return render(request, 'admin-app/ventas/lista.html', {'ventas': ventas})

@staff_required
def ventas_detalle(request, id):
    venta = get_object_or_404(Ventas, id_venta=id)
    detalles = DetalleVenta.objects.filter(venta=venta)
    return render(request, 'admin-app/ventas/detalle.html', {'venta': venta, 'detalles': detalles})

@staff_required
def ventas_actualizar_estado(request, id):
    venta = get_object_or_404(Ventas, id_venta=id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Ventas.ESTADO_CHOICES).keys():
            venta.estado = nuevo_estado
            venta.save()
            messages.success(request, 'Estado actualizado correctamente')
        return redirect('ventas_lista')
    return (render(request, 'admin-app/ventas/detalle.html', {'venta': venta, 'detalles': DetalleVenta.objects.filter(venta=venta)}))

def admin_login(request):
    """Login especial para administradores"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(request, f'¡Bienvenido Administrador {user.username}!')
                return redirect('inicio')
            else:
                messages.error(request, 'Acceso solo para administradores')
                return redirect('admin_login')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'admin_login.html')

def cliente_login(request):
    """Login para clientes"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido/a {user.username}!')
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'cliente_login.html')


# Vista para productos por marca
def productos_marca(request, marca_id):
    marca = get_object_or_404(Marcas, id=marca_id)
    productos = Productos.objects.filter(marca=marca, stock__gt=0)
    
    return render(request, 'productos/marca.html', {
        'marca': marca,
        'productos': productos,
        'categorias': Categorias.objects.filter(productos__marca=marca).distinct()
    })

# Vista para productos por marca y categoría
def productos_marca_categoria(request, marca_id, categoria_id):
    marca = get_object_or_404(Marcas, id=marca_id)
    categoria = get_object_or_404(Categorias, id=categoria_id)
    
    productos = Productos.objects.filter(
        marca=marca,
        categoria=categoria,
        stock__gt=0
    )
    
    return render(request, 'productos/marca_categoria.html', {
        'marca': marca,
        'categoria': categoria,
        'productos': productos
    })