from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import Perfil

def get_role_choices():
    """
    Obtiene los roles (grupos) desde la base de datos para usarlos en el formulario.
    """
    try:
        # Excluimos roles que no queremos que se puedan asignar en el registro si es necesario
        return [(group.name, group.name.capitalize()) for group in Group.objects.all()]
    except Exception:
        # Si la base de datos no está lista (ej. durante migraciones), devuelve una lista vacía.
        return []

class CustomUserCreationForm(UserCreationForm):
    """
    Formulario personalizado para la creación de usuarios que incluye campos del perfil.
    """
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}))
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}))
    rol = forms.ChoiceField(choices=get_role_choices, required=True, widget=forms.Select(attrs={'class': 'form-select'}))
    telefono = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono (Opcional)'}))
    direccion = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección (Opcional)'}))
    # Sobreescribimos los campos de contraseña para aplicarles el estilo de Bootstrap.
    password1 = forms.CharField(label="Contraseña", required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))
    password2 = forms.CharField(label="Confirmar Contraseña", required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}))
    imagen = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'd-none', 'id': 'id_imagen', 'accept': 'image/*'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')
        # Los widgets para los campos heredados de UserCreationForm (username, password) se quedan aquí.
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        }
        
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        
        if commit:
            user.save()
            # Asignar rol
            from django.contrib.auth.models import Group
            rol_name = self.cleaned_data.get('rol')
            if rol_name:
                grupo, created = Group.objects.get_or_create(name=rol_name)
                user.groups.add(grupo)

            # Crear o actualizar perfil
            Perfil.objects.update_or_create(
                user=user,
                defaults={
                    'telefono': self.cleaned_data.get('telefono'),
                    'direccion': self.cleaned_data.get('direccion'),
                    'imagen': self.cleaned_data.get('imagen')
                }
            )
        return user

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
        }

class PerfilUpdateForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['telefono', 'direccion', 'imagen']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'imagen': forms.FileInput(attrs={'class': 'd-none', 'id': 'id_imagen', 'accept': 'image/*'}),
        }