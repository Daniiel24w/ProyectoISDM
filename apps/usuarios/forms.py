from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.db import transaction

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, required=True, label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '})
    )
    last_name = forms.CharField(
        max_length=150, required=True, label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '})
    )
    email = forms.EmailField(
        max_length=254, required=True, label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': ' '})
    )
    telefono = forms.CharField(
        max_length=20, required=False, label='Teléfono (Opcional)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '})
    )

    # Campo para seleccionar el rol (grupo) del usuario
    rol = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label="Rol de Usuario",
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Seleccione el rol del nuevo usuario."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'telefono')
        # Personalizamos los widgets para los campos de contraseña
        widgets = {
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ' '}),
        }

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        # Guardamos los datos adicionales
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        # NOTA: El campo 'telefono' no se guarda en el modelo User por defecto.
        # Para guardarlo, necesitaríamos crear un modelo 'Perfil' asociado al usuario.
        # Por ahora, el campo existe en el formulario pero no se persiste.
        if commit:
            user.save()
            # Asignamos el grupo (rol) seleccionado al usuario
            rol_seleccionado = self.cleaned_data.get('rol')
            user.groups.add(rol_seleccionado)
        return user