from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from .forms import CustomUserCreationForm, UserUpdateForm, PerfilUpdateForm

class CustomLoginView(LoginView):
    """
    Vista personalizada para el login de usuarios.
    """
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True
    # Django usará LOGIN_REDIRECT_URL de settings.py para redirigir
    # al usuario después de un inicio de sesión exitoso.

@login_required
def perfil_view(request):
    """
    Muestra la página de perfil del usuario logueado.
    """
    # Pasamos el objeto 'user' (que ya está disponible a través de request)
    # y su perfil asociado al contexto de la plantilla.
    return render(request, 'usuarios/perfil.html', {'perfil': request.user.perfil})

@login_required
@transaction.atomic
def edit_perfil_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        perfil_form = PerfilUpdateForm(request.POST, request.FILES, instance=request.user.perfil)
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado exitosamente!')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        perfil_form = PerfilUpdateForm(instance=request.user.perfil)

    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'perfil': request.user.perfil  # Para la imagen de perfil
    }
    return render(request, 'usuarios/edit-perfil.html', context)

def es_desarrollador(user):
    """
    Función de prueba para verificar si un usuario pertenece al grupo 'desarrollador'.
    """
    return user.groups.filter(name='desarrollador').exists()

@login_required
@user_passes_test(es_desarrollador, login_url=reverse_lazy('core:index'))
def registro_view(request):
    """
    Vista para que un desarrollador pueda registrar nuevos usuarios.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'¡La cuenta para "{username}" ha sido creada exitosamente!')
            return redirect('core:index') # Redirige al panel principal tras el éxito
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})