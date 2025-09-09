from django.shortcuts import redirect
from django.contrib import messages

class BlockInactiveUserMiddleware:
    """
    Если пользователь заблокирован (is_active=False), разлогиниваем и не даём ходить по сайту.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        u = getattr(request, "user", None)
        if u and u.is_authenticated and not u.is_active and request.path != "/users/logout/":
            from django.contrib.auth import logout
            logout(request)
            messages.error(request, "Ваш аккаунт заблокирован.")
            return redirect("users:login")
        return self.get_response(request)
