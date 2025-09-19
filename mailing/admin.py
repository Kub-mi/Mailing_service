from django.contrib import admin
from .models import Client, Message, Mailing, Attempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "owner")
    list_filter = ("owner",)
    search_fields = ("email", "full_name")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "owner")
    search_fields = ("subject", "body", "owner__email")
    list_filter = ("owner",)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "start_at", "finish_at", "message", "owner")
    list_filter = ("status", "owner")
    search_fields = ("id", "message__subject", "owner__email")
    filter_horizontal = ("recipients",)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "status", "mailing", "client")
    list_filter = ("status", "created_at")
    search_fields = ("server_response", "mailing__id", "client__email")
    autocomplete_fields = ("mailing", "client")
