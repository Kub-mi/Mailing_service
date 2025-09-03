from django import forms
from .models import Client, Message, Mailing


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["email", "full_name", "comment"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "user@example.com"}),
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Иванов Иван"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Комментарий"}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["subject", "body"]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Тема письма"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 6, "placeholder": "Текст сообщения"}),
        }


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ["start_at", "finish_at", "status", "message", "recipients"]
        widgets = {
            "start_at": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "finish_at": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "message": forms.Select(attrs={"class": "form-select"}),
            "recipients": forms.SelectMultiple(attrs={"class": "form-select", "size": 8}),
        }

        def clean(self):
            data = super().clean()
            start_at = data.get("start_at")
            finish_at = data.get("finish_at")
            if start_at and finish_at and finish_at <= start_at:
                raise forms.ValidationError("Дата окончания должна быть позже даты начала.")
            return data
