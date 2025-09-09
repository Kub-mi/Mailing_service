from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages as dj_messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime

from .mixins import OwnerFilteredQuerysetMixin, OwnerOrManagerRequiredMixin
from .models import Client, Message, Mailing, Attempt
from .forms import ClientForm, MessageForm, MailingForm
from .services import send_mailing


PERM_VIEW_ALL = "mailing.view_all_clients"
PERM_VIEW_ALL_MESSAGES = "mailing.view_all_messages"
PERM_VIEW_ALL_MAILINGS = "mailing.view_all_mailings"


class ClientListView(LoginRequiredMixin, OwnerFilteredQuerysetMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL):
            return qs
        return qs.filter(owner=self.request.user)


class ClientDetailView(LoginRequiredMixin, OwnerFilteredQuerysetMixin, DetailView):
    model = Client
    template_name = 'mailing/client_detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL):
            return qs
        return qs.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, OwnerOrManagerRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL):
            return qs
        return qs.filter(owner=self.request.user)


class ClientDeleteView(LoginRequiredMixin, OwnerOrManagerRequiredMixin, DeleteView):
    model = Client
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL):
            return qs
        return qs.filter(owner=self.request.user)


class MessageListView(LoginRequiredMixin, OwnerFilteredQuerysetMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'message'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL_MESSAGES):
            return qs
        return qs.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, OwnerFilteredQuerysetMixin, DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL_MESSAGES):
            return qs
        return qs.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, OwnerOrManagerRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL_MESSAGES):
            return qs
        return qs.filter(owner=self.request.user)


class MessageDeleteView(LoginRequiredMixin, OwnerOrManagerRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL_MESSAGES):
            return qs
        return qs.filter(owner=self.request.user)


class MailingListView(LoginRequiredMixin, OwnerFilteredQuerysetMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"
    paginate_by = 10

    def get_queryset(self):
        qs = (super()
              .get_queryset()
              .select_related("message", "owner")
              .prefetch_related("recipients"))
        if self.request.user.has_perm(PERM_VIEW_ALL_MAILINGS):
            return qs
        return qs.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, OwnerFilteredQuerysetMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"

    def get_queryset(self):
        qs = (super()
              .get_queryset()
              .select_related("message", "owner")
              .prefetch_related("recipients"))
        if self.request.user.has_perm(PERM_VIEW_ALL_MAILINGS):
            return qs
        return qs.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        m = self.object
        attempts = m.attempts.all()
        ctx["attempts_total"] = attempts.count()
        ctx["attempts_success"] = attempts.filter(status="Успешно").count()
        ctx["attempts_failed"] = attempts.filter(status="Не успешно").count()
        return ctx


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        form.save_m2m()
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, OwnerOrManagerRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL_MAILINGS):
            return qs
        return qs.filter(owner=self.request.user)


class MailingDeleteView(LoginRequiredMixin, OwnerOrManagerRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/confirm_delete.html"  # можно общий шаблон удаления
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL_MAILINGS):
            return qs
        return qs.filter(owner=self.request.user)


@login_required
def send_mailing_view(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    if (mailing.owner_id != request.user.id) and (not request.user.has_perm('mailing.view_all_mailings')):
        dj_messages.error(request, 'Нет доступа к этой рассылке')
        return redirect('mailing:mailing_list')

    sent_ok, total = send_mailing(mailing)
    dj_messages.success(request, f'Отправлено {sent_ok} из {total}.')
    return redirect(reverse('mailing:mailingdetail', args=[mailing/pk]))


class AttemptListView(LoginRequiredMixin, ListView):
    model = Attempt
    template_name = "mailing/attempt_list.html"
    context_object_name = "attempts"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("mailing", "client", "mailing__owner")
        # менеджер видит всё (по пермишену на рассылки), обычный — только свои (по owner рассылки)
        if self.request.user.has_perm("mailing.view_all_mailings"):
            return qs
        return qs.filter(mailing__owner=self.request.user)


class AttemptByMailingView(LoginRequiredMixin, ListView):
    model = Attempt
    template_name = "mailing/attempt_list.html"
    context_object_name = "attempts"
    paginate_by = 20

    def get_queryset(self):
        mailing_id = self.kwargs["pk"]
        qs = (super()
              .get_queryset()
              .filter(mailing_id=mailing_id)
              .select_related("mailing", "client", "mailing__owner"))
        if self.request.user.has_perm("mailing.view_all_mailings"):
            return qs
        return qs.filter(mailing__owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mailing_id"] = self.kwargs["pk"]
        return ctx


class StatsView(LoginRequiredMixin, TemplateView):
    template_name = "mailing/stats.html"

    def get_queryset_base(self, request):
        """
        Базовый queryset рассылок под текущего пользователя.
        Менеджер (если есть право просмотра всех) видит все.
        """
        qs = Mailing.objects.all()
        if not request.user.has_perm("mailing.view_all_mailings"):
            qs = qs.filter(owner=request.user)
        return qs

    def get_date_bounds(self):
        """
        Читаем GET-параметры ?from=YYYY-MM-DD&to=YYYY-MM-DD
        и возвращаем (date_from, date_to) в tz-aware границах.
        """
        date_from_str = self.request.GET.get("from")
        date_to_str = self.request.GET.get("to")

        date_from = None
        date_to = None

        if date_from_str:
            try:
                d = datetime.strptime(date_from_str, "%Y-%m-%d")
                date_from = timezone.make_aware(datetime(d.year, d.month, d.day, 0, 0, 0))
            except Exception:
                pass

        if date_to_str:
            try:
                d = datetime.strptime(date_to_str, "%Y-%m-%d")
                # включаем весь день до 23:59:59
                date_to = timezone.make_aware(datetime(d.year, d.month, d.day, 23, 59, 59))
            except Exception:
                pass

        return date_from, date_to

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        request = self.request

        mailings_qs = self.get_queryset_base(request)

        # Счётчики верхнего уровня
        total_mailings = mailings_qs.count()
        active_mailings = mailings_qs.filter(status="Запущена").count()
        total_messages = Message.objects.filter(
            owner=request.user if not request.user.has_perm("mailing.view_all_mailings") else None
        )
        if hasattr(total_messages, "filter"):  # если None — вернётся Manager
            total_messages = total_messages.filter(owner=request.user)
        total_messages = total_messages.count() if hasattr(total_messages, "count") else Message.objects.count()

        # Дата-фильтры для попыток
        date_from, date_to = self.get_date_bounds()
        attempts_filter = Q(mailing__in=mailings_qs)
        if date_from:
            attempts_filter &= Q(created_at__gte=date_from)  # поле даты в Attempt — поправь, если у тебя другое
        if date_to:
            attempts_filter &= Q(created_at__lte=date_to)

        # Агрегация по попыткам в целом
        agg = Attempt.objects.filter(attempts_filter).aggregate(
            attempts_total=Count("id"),
            attempts_success=Count("id", filter=Q(status="Успешно")),
            attempts_failed=Count("id", filter=Q(status="Не успешно")),
        )

        # Разбивка по каждой рассылке
        per_mailing = mailings_qs.annotate(
            attempts_total=Count("attempts", filter=Q(attempts__in=Attempt.objects.filter(attempts_filter))),
            attempts_success=Count("attempts", filter=Q(attempts__in=Attempt.objects.filter(attempts_filter), attempts__status="Успешно")),
            attempts_failed=Count("attempts", filter=Q(attempts__in=Attempt.objects.filter(attempts_filter), attempts__status="Не успешно")),
        ).select_related("message").order_by("-id")

        ctx.update({
            "total_mailings": total_mailings,
            "active_mailings": active_mailings,
            "total_messages": total_messages,
            "attempts_total": agg.get("attempts_total", 0) or 0,
            "attempts_success": agg.get("attempts_success", 0) or 0,
            "attempts_failed": agg.get("attempts_failed", 0) or 0,
            "per_mailing": per_mailing,
            "date_from": self.request.GET.get("from", ""),
            "date_to": self.request.GET.get("to", ""),
        })
        return ctx
