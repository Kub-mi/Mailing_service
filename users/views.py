from django.contrib import messages as dj_messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import CreateView, View, TemplateView
from django.conf import settings
from django.core.mail import send_mail

from .forms import SignUpForm

User = get_user_model()


class SignUpView(CreateView):
    template_name = "users/register.html"
    form_class = SignUpForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        # Блокируем вход до подтверждения
        user.is_active = False
        user.username = user.email  # если нужно для совместимости
        user.save()

        # Шлём письмо с подтверждением
        self.send_activation_email(user)
        dj_messages.success(self.request, "Мы отправили письмо с подтверждением на ваш email.")
        return super().form_valid(form)

    def send_activation_email(self, user):
        from django.core.mail import send_mail
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        link = self.request.build_absolute_uri(
            reverse("users:confirm_email", kwargs={"uidb64": uid, "token": token})
        )
        subject = "Подтверждение регистрации"
        message = (
            f"Здравствуйте, {user.first_name or ''}\n\n"
            f"Для подтверждения email перейдите по ссылке:\n{link}\n\n"
            f"Если вы не регистрировались — просто игнорируйте это письмо."
        )
        send_mail(subject, message, None, [user.email], fail_silently=False)


class ConfirmEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except Exception:
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save(update_fields=["is_active"])
            dj_messages.success(request, "Email подтверждён. Теперь вы можете войти.")
            return redirect("users:login")
        dj_messages.error(request, "Ссылка недействительна или устарела.")
        return redirect("pages:home")


class ProfileView(TemplateView):
    """
    Заглушка на будущее (п. интерфейса профиля).
    """
    template_name = "users/profile.html"
def send_activation_email(self, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    link = self.request.build_absolute_uri(
        reverse("users:confirm_email", kwargs={"uidb64": uid, "token": token})
    )
    subject = "Подтверждение регистрации"
    message = (
        f"Здравствуйте, {user.first_name or ''}\n\n"
        f"Для подтверждения email перейдите по ссылке:\n{link}\n\n"
        f"Если вы не регистрировались — просто игнорируйте это письмо."
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        # Не валим 500, а показываем подсказку
        dj_messages.error(self.request, f"Не удалось отправить письмо: {e}. Проверьте настройки почты.")
