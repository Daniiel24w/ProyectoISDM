from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

@never_cache
@login_required
def index_view(request):
    """
    Renderiza la página principal (dashboard) del sitio.
    """
    return render(request, 'core/index.html')
