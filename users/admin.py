from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "username", "is_active", "is_staff")
    ordering = ("email",)
    fieldsets = UserAdmin.fieldsets + (
        ("Дополнительно", {"fields": ("phone", "avatar", "country")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets
