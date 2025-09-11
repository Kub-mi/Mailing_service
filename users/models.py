from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="Телефон"
    )
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Аватар"
    )
    country = models.CharField(max_length=64, blank=True, verbose_name="Страна")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # username просит Django для AbstractUser

    def __str__(self):
        # чтобы в админке и логах был наглядный вывод
        return self.email or self.username

    class Meta:
        permissions = [
            ("view_user_list", "Может просматривать список пользователей"),
            ("block_users", "Может блокировать/разблокировать пользователей"),
        ]
