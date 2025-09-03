from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages as dj_messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Client, Message, Mailing
from .forms import ClientForm, MessageForm, MailingForm
from .services import send_mailing


PERM_VIEW_ALL = "mailing.view_all_clients"
PERM_VIEW_ALL_MESSAGES = "mailing.view_all_messages"
PERM_VIEW_ALL_MAILINGS = "mailing.view_all_mailings"


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL):
            return qs
        return qs.filter(owner=self.request.user)


class ClientDetailView(LoginRequiredMixin, DetailView):
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


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL):
            return qs
        return qs.filter(owner=self.request.user)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL):
            return qs
        return qs.filter(owner=self.request.user)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'message'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL_MESSAGES):
            return qs
        return qs.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, DetailView):
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


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL_MESSAGES):
            return qs
        return qs.filter(owner=self.request.user)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL_MESSAGES):
            return qs
        return qs.filter(owner=self.request.user)


class MailingListView(LoginRequiredMixin, ListView):
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


class MailingDetailView(LoginRequiredMixin, DetailView):
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


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL_MAILINGS):
            return qs
        return qs.filter(owner=self.request.user)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
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
