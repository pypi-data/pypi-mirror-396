from django.shortcuts import redirect
from functools import wraps
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

def aluno_login_required(view_func):
	@wraps(view_func)
	def wrapper(request, *args, **kwargs):
		if not request.session.get("aluno_sso"):
			return redirect("/")  # antes era: return redirect("/login-sso/")
		return view_func(request, *args, **kwargs)
	return wrapper





def exportacao_permission_required(permission):
    """
    Decorador que verifica se o usuário tem a permissão específica ou é admin.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Admin sempre tem acesso
            if request.user.is_staff or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verificar permissão específica
            if request.user.has_perm(permission):
                return view_func(request, *args, **kwargs)
                
            return HttpResponseForbidden("Você não tem permissão para acessar esta funcionalidade.")
            
        return _wrapped_view
    
    return decorator