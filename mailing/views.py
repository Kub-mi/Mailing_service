from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.core.cache import cache
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    TemplateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime
from django.views.decorators.vary import vary_on_cookie

from .mixins import OwnerFilteredQuerysetMixin, OwnerOrManagerRequiredMixin
from .models import Client, Message, Mailing, Attempt
from .forms import ClientForm, MessageForm, MailingForm
from .services import send_mailing


PERM_VIEW_ALL = "mailing.view_all_clients"
PERM_VIEW_ALL_MESSAGES = "mailing.view_all_messages"
PERM_VIEW_ALL_MAILINGS = "mailing.view_all_mailings"


class ClientListView(LoginRequiredMixin, OwnerFilteredQuerysetMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL):
            return qs
        return qs.filter(owner=self.request.user)


class ClientDetailView(LoginRequiredMixin, OwnerFilteredQuerysetMixin, DetailView):
    model = Client
    template_name = "mailing/client_detail.html"

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
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL):
            return qs
        return qs.filter(owner=self.request.user)


class ClientDeleteView(LoginRequiredMixin, OwnerOrManagerRequiredMixin, DeleteView):
    model = Client
    template_name = "mailing/confirm_delete.html"
    success_url = reverse_lazy("mailing:client_list")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL):
            return qs
        return qs.filter(owner=self.request.user)


class MessageListView(LoginRequiredMixin, OwnerFilteredQuerysetMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "message"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL_MESSAGES):
            return qs
        return qs.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, OwnerFilteredQuerysetMixin, DetailView):
    model = Message
    template_name = "mailing/message_detail.html"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL_MESSAGES):
            return qs
        return qs.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, OwnerOrManagerRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL_MESSAGES):
            return qs
        return qs.filter(owner=self.request.user)


class MessageDeleteView(LoginRequiredMixin, OwnerOrManagerRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")

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
        qs = (
            super()
            .get_queryset()
            .select_related("message", "owner")
            .prefetch_related("recipients")
        )
        if self.request.user.has_perm(PERM_VIEW_ALL_MAILINGS):
            return qs
        return qs.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, OwnerFilteredQuerysetMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("message", "owner")
            .prefetch_related("recipients")
        )
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
    template_name = "mailing/confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL_MAILINGS):
            return qs
        return qs.filter(owner=self.request.user)


@login_required
def send_mailing_view(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    # запрет отправки отключенной рассылки
    if not mailing.is_enabled:
        messages.error(request, "Эта рассылка отключена менеджером.")
        return redirect("mailing:mailing_detail", pk=pk)

    # проверка доступа: владелец или менеджер
    if (mailing.owner_id != request.user.id) and (
        not request.user.has_perm("mailing.view_all_mailings")
    ):
        messages.error(request, "Нет доступа к этой рассылке")
        return redirect("mailing:mailing_list")

    sent_ok, total = send_mailing(mailing)
    messages.success(request, f"Отправлено {sent_ok} из {total}.")
    return redirect("mailing:mailing_detail", pk=pk)


@method_decorator(
    [vary_on_cookie, cache_page(60, key_prefix="attempts")], name="dispatch"
)
class AttemptListView(LoginRequiredMixin, ListView):
    model = Attempt
    template_name = "mailing/attempt_list.html"
    context_object_name = "attempts"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            super().get_queryset().select_related("mailing", "client", "mailing__owner")
        )
        # менеджер видит всё, обычный — только свои (по owner рассылки)
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
        qs = (
            super()
            .get_queryset()
            .filter(mailing_id=mailing_id)
            .select_related("mailing", "client", "mailing__owner")
        )
        if self.request.user.has_perm("mailing.view_all_mailings"):
            return qs
        return qs.filter(mailing__owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mailing_id"] = self.kwargs["pk"]
        return ctx


@method_decorator(
    cache_control(no_cache=True, no_store=True, must_revalidate=True), name="dispatch"
)
class StatsView(LoginRequiredMixin, TemplateView):
    template_name = "mailing/stats.html"

    def _get_queryset_base(self, request):
        """
        Базовый queryset рассылок под текущего пользователя.
        Менеджер (если есть право просмотра всех) видит все.
        """
        qs = Mailing.objects.all()
        if not request.user.has_perm("mailing.view_all_mailings"):
            qs = qs.filter(owner=request.user)
        return qs

    def _get_date_bounds(self):
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
                date_from = timezone.make_aware(
                    datetime(d.year, d.month, d.day, 0, 0, 0)
                )
            except Exception:
                pass

        if date_to_str:
            try:
                d = datetime.strptime(date_to_str, "%Y-%m-%d")
                # включаем весь день до 23:59:59
                date_to = timezone.make_aware(
                    datetime(d.year, d.month, d.day, 23, 59, 59)
                )
            except Exception:
                pass

        return date_from, date_to

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        date_from_param = self.request.GET.get("from", "")
        date_to_param = self.request.GET.get("to", "")

        # ключ кеша только для агрегатов (не кладём QuerySet)
        cache_key = f"stats:{user.id}:{date_from_param}:{date_to_param}"
        cached = cache.get(cache_key)
        if cached:
            ctx.update(cached)
            # отдельно считаем per_mailing «вживую», чтобы шаблон работал как раньше
            mailings_qs = self._get_queryset_base(self.request)
            date_from, date_to = self._get_date_bounds()
            attempts_filter = Q(mailing__in=mailings_qs)
            if date_from:
                attempts_filter &= Q(created_at__gte=date_from)
            if date_to:
                attempts_filter &= Q(created_at__lte=date_to)
            per_mailing = (
                mailings_qs.annotate(
                    attempts_total=Count(
                        "attempts",
                        filter=Q(attempts__in=Attempt.objects.filter(attempts_filter)),
                    ),
                    attempts_success=Count(
                        "attempts",
                        filter=Q(
                            attempts__in=Attempt.objects.filter(attempts_filter),
                            attempts__status="Успешно",
                        ),
                    ),
                    attempts_failed=Count(
                        "attempts",
                        filter=Q(
                            attempts__in=Attempt.objects.filter(attempts_filter),
                            attempts__status="Не успешно",
                        ),
                    ),
                )
                .select_related("message")
                .order_by("-id")
            )
            ctx["per_mailing"] = per_mailing
            return ctx

        # нет кеша — считаем всё
        mailings_qs = self._get_queryset_base(self.request)
        total_mailings = mailings_qs.count()
        active_mailings = mailings_qs.filter(status="Запущена").count()

        if self.request.user.has_perm("mailing.view_all_messages"):
            total_messages = Message.objects.count()
        else:
            total_messages = Message.objects.filter(owner=user).count()

        date_from, date_to = self._get_date_bounds()
        attempts_filter = Q(mailing__in=mailings_qs)
        if date_from:
            attempts_filter &= Q(created_at__gte=date_from)
        if date_to:
            attempts_filter &= Q(created_at__lte=date_to)

        agg = Attempt.objects.filter(attempts_filter).aggregate(
            attempts_total=Count("id"),
            attempts_success=Count("id", filter=Q(status="Успешно")),
            attempts_failed=Count("id", filter=Q(status="Не успешно")),
        )

        per_mailing = (
            mailings_qs.annotate(
                attempts_total=Count(
                    "attempts",
                    filter=Q(attempts__in=Attempt.objects.filter(attempts_filter)),
                ),
                attempts_success=Count(
                    "attempts",
                    filter=Q(
                        attempts__in=Attempt.objects.filter(attempts_filter),
                        attempts__status="Успешно",
                    ),
                ),
                attempts_failed=Count(
                    "attempts",
                    filter=Q(
                        attempts__in=Attempt.objects.filter(attempts_filter),
                        attempts__status="Не успешно",
                    ),
                ),
            )
            .select_related("message")
            .order_by("-id")
        )

        # кладём в кеш только сериализуемые агрегаты
        payload = {
            "total_mailings": total_mailings,
            "active_mailings": active_mailings,
            "total_messages": total_messages,
            "attempts_total": agg.get("attempts_total", 0) or 0,
            "attempts_success": agg.get("attempts_success", 0) or 0,
            "attempts_failed": agg.get("attempts_failed", 0) or 0,
            "date_from": date_from_param,
            "date_to": date_to_param,
        }
        cache.set(cache_key, payload, timeout=60)  # 1 минута

        ctx.update(payload)
        ctx["per_mailing"] = per_mailing
        return ctx


# --------- MANAGER TOGGLE ---------
@login_required
@permission_required("mailing.disable_mailings", raise_exception=True)
def mailing_toggle_enable(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.is_enabled = not mailing.is_enabled
    mailing.save(update_fields=["is_enabled"])
    messages.success(
        request,
        f"Рассылка #{mailing.pk} теперь {'включена' if mailing.is_enabled else 'отключена'}.",
    )
    return redirect("mailing:mailing_detail", pk=pk)
