# app_sabritas/forms.py - VERSIÓN CORREGIDA
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class RegistroForm(UserCreationForm):
    # Campos adicionales para el registro
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        })
    )
    nombre = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
    )
    apellido = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido'
        })
    )
    telefono = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+52 55 1234 5678'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'nombre', 'apellido', 'telefono', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar los campos existentes
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario único'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Crea una contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Repite la contraseña'
        })
        # Remover ayuda de validación
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['username'].help_text = ''
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['nombre']
        user.last_name = self.cleaned_data['apellido']
        
        if commit:
            user.save()
            
            # Crear o actualizar el cliente asociado
            Clientes.objects.update_or_create(
                usuario=user,
                defaults={
                    'nombre': self.cleaned_data['nombre'],
                    'apellido': self.cleaned_data['apellido'],
                    'email': self.cleaned_data['email'],
                    'telefono': self.cleaned_data['telefono']
                }
            )
        
        return user
    
class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marcas
        fields = ['nombre', 'descripcion', 'logo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la marca'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la marca'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

# ========== FORMULARIOS DE CATEGORÍAS ==========
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categorias
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la categoría'
            })
        }

# ========== FORMULARIOS DE PRODUCTOS ==========
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = [
            'nombre', 'descripcion', 'precio', 'stock',
            'imagen', 'marca', 'categoria', 'peso', 'sabor'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del producto'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'marca': forms.Select(attrs={
                'class': 'form-control'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'peso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 50g, 100g, 250g'
            }),
            'sabor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Natural, Queso, Chile Limón'
            })
        }

# ========== FORMULARIOS DE CLIENTES ==========
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = ['nombre', 'apellido', 'email', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido del cliente'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 555-123-4567'
            })
        }

class ClienteAdminForm(forms.ModelForm):
    # Para admin, permite asignar usuario
    usuario = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Clientes
        fields = ['usuario', 'nombre', 'apellido', 'email', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'})
        }

# ========== FORMULARIOS DE CARRITO ==========
class CarritoItemForm(forms.ModelForm):
    class Meta:
        model = CarritoItem
        fields = ['cantidad']
        widgets = {
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'style': 'width: 80px;'
            })
        }

# ========== FORMULARIOS DE VENTAS ==========
class VentaForm(forms.ModelForm):
    class Meta:
        model = Ventas
        fields = ['estado', 'direccion_envio', 'metodo_pago']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'direccion_envio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa de envío'
            }),
            'metodo_pago': forms.Select(attrs={
                'class': 'form-control',
                'choices': [
                    ('tarjeta', 'Tarjeta de crédito'),
                    ('paypal', 'PayPal'),
                    ('efectivo', 'Efectivo'),
                    ('transferencia', 'Transferencia bancaria')
                ]
            })
        }

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        }

# ========== FORMULARIOS DE BÚSQUEDA ==========
class BusquedaProductoForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar productos...'
        })
    )
    categoria = forms.ModelChoiceField(
        queryset=Categorias.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    marca = forms.ModelChoiceField(
        queryset=Marcas.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_precio = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Precio mínimo',
            'step': '0.01'
        })
    )
    max_precio = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Precio máximo',
            'step': '0.01'
        })
    )

# ========== FORMULARIO DE CONTACTO ==========
class ContactoForm(forms.Form):
    nombre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Tu nombre'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'correo@ejemplo.com'
    }))
    asunto = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Asunto del mensaje'
    }))
    mensaje = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 4,
        'placeholder': 'Escribe tu mensaje aquí...'
    }))