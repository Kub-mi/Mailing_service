from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignUpView, ConfirmEmailView
from .forms import EmailLoginForm

app_name = "users"

urlpatterns = [
    # аутентификация
    path("login/", auth_views.LoginView.as_view(
        template_name="users/login.html",
        authentication_form=EmailLoginForm,
    ), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # регистрация + подтверждение
    path("register/", SignUpView.as_view(), name="register"),
    path("confirm/<uidb64>/<token>/", ConfirmEmailView.as_view(), name="confirm_email"),

    # восстановление пароля (встроенные вьюхи)
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="users/password_reset_form.html",
        email_template_name="users/password_reset_email.txt",
        subject_template_name="users/password_reset_subject.txt",
        success_url="/users/password-reset/done/",
    ), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="users/password_reset_done.html",
    ), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="users/password_reset_confirm.html",
        success_url="/users/reset/complete/",
    ), name="password_reset_confirm"),
    path("reset/complete/", auth_views.PasswordResetCompleteView.as_view(
        template_name="users/password_reset_complete.html",
    ), name="password_reset_complete"),
]
