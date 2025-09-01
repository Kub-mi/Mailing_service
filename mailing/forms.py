from django import forms
from .models import Client, Message, Mailing


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["email", "full_name", "comment"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["subject", "body"]


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ["start_at", "finish_at", "status", "message", "recipients"]
        widgets = {
            "start_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "finish_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

        def clean(self):
            data = super().clean()
            start_at = data.get("start_at")
            finish_at = data.get("finish_at")
            if start_at and finish_at and finish_at <= start_at:
                raise forms.ValidationError("Дата окончания должна быть позже даты начала.")
            return data
