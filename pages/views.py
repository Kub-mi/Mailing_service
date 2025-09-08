from django.views.generic import TemplateView
from mailing.models import Mailing, Client


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Всего рассылок
        total_mailings = Mailing.objects.count()

        # Активные (со статусом "Запущена")
        running_status = getattr(Mailing, "STATUS_RUNNING", "Запущена")
        active_mailings = Mailing.objects.filter(status=running_status).count()

        # Уникальные получатели (по email)
        unique_recipients = Client.objects.values("email").distinct().count()

        ctx.update({
            "total_mailings": total_mailings,
            "active_mailings": active_mailings,
            "unique_recipients": unique_recipients,
        })
        return ctx
