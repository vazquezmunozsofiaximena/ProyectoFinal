# app_sabritas/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Clientes

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
                alergias="",  # Vacío ahora
                preferencias=""  # Vacío ahora
            )