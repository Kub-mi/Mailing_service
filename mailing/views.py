from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Client, Message
from .forms import ClientForm, MessageForm


PERM_VIEW_ALL = "mailing.view_all_clients"
PERM_VIEW_ALL_MESSAGES = "mailing.view_all_messages"

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


class ClientDeliteView(LoginRequiredMixin, DeleteView):
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
    template_name = 'mailing/message_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(PERM_VIEW_ALL_MESSAGES):
            return qs
        return qs.filter(owner=self.request.user)