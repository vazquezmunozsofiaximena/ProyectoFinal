# app_sabritas/models.py - VERSIÓN DEFINITIVA
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password

class Marcas(models.Model):
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='marcas/', null=True, blank=True)
    descripcion = models.TextField()
    
    def __str__(self):
        return self.nombre

class Categorias(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    
    def __str__(self):
        return self.nombre

class Productos(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    marca = models.ForeignKey(Marcas, on_delete=models.CASCADE, related_name='productos')
    categoria = models.ForeignKey(Categorias, on_delete=models.CASCADE, related_name='productos')
    peso = models.CharField(max_length=50, help_text="Ej: 50g, 100g, 250g")
    sabor = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre
    
    def tiene_stock(self):
        return self.stock > 0

class Clientes(models.Model):
    id_clientes = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cliente')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telefono = models.CharField(max_length=15)
    fecha_registro = models.DateField(auto_now_add=True)
    
    def __str__(self):
        if self.usuario:
            return f"{self.nombre} {self.apellido} ({self.usuario.username})"
        return f"{self.nombre} {self.apellido}"
    
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
@receiver(post_save, sender=User)
def crear_cliente_desde_usuario(sender, instance, created, **kwargs):
    """
    Crear automáticamente un registro en Clientes cuando se crea un nuevo User
    Solo si no existe ya un cliente para este usuario
    """
    if created and not instance.is_staff:
        # Verificar si ya existe un cliente (por si el formulario ya lo creó)
        if not hasattr(instance, 'cliente'):
            Clientes.objects.create(
                usuario=instance,
                nombre=instance.first_name if instance.first_name else instance.username,
                apellido=instance.last_name if instance.last_name else "Usuario",
                email=instance.email,
                telefono="Por definir",
            )


class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carritos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0.16)
    
    def __str__(self):
        return f"Carrito de {self.usuario.username}"
    
    def subtotal_carrito(self):
        total = 0
        for item in self.items.all():
            total += item.subtotal()
        return total
    
    def calcular_iva(self):
        return self.subtotal_carrito() * self.iva
    
    def total_con_iva(self):
        return self.subtotal_carrito() * (1 + self.iva)
    
    def total_items(self):
        return sum(item.cantidad for item in self.items.all())

class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
    def subtotal(self):
        return self.producto.precio * self.cantidad

class Ventas(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    id_venta = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compras')
    fecha_venta = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    direccion_envio = models.TextField()
    metodo_pago = models.CharField(max_length=50, default='Tarjeta de crédito')
    
    def __str__(self):
        return f"Venta #{self.id_venta} - {self.cliente.username}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Ventas, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)