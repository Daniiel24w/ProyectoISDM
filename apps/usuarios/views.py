from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .forms import CustomUserCreationForm

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
    # Aquí puedes pasar el objeto 'user' al contexto si necesitas más datos
    return render(request, 'usuarios/perfil.html')

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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'¡La cuenta para "{username}" ha sido creada exitosamente!')
            return redirect('core:index') # Redirige al panel principal tras el éxito
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})