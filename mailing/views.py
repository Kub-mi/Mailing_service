from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Client
from .forms import ClientForm


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/client.html'
    context_object_name = 'clients'
    paginate_by = 10
    manager_perm = 'mailing.views_all_clients'


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'mailing/client_detail.html'
    manager_perm = 'mailing.views_all_clients'


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')
    manager_perm = 'mailing.views_all_clients'


class ClientDeliteView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:client_list')
    manager_perm = 'mailing.views_all_clients'

