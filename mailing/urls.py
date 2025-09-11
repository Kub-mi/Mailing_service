from django.urls import path
from .views import (
    ClientListView,
    ClientDetailView,
    ClientCreateView,
    ClientUpdateView,
    ClientDeleteView,
    MessageListView,
    MessageDetailView,
    MessageCreateView,
    MessageUpdateView,
    MessageDeleteView,
    MailingListView,
    MailingCreateView,
    MailingDetailView,
    MailingUpdateView,
    MailingDeleteView,
    send_mailing_view,
    AttemptListView,
    AttemptByMailingView,
)
from .views import StatsView, mailing_toggle_enable

app_name = "mailing"

urlpatterns = [
    # Clients
    path("clients/", ClientListView.as_view(), name="client_list"),
    path("clients/create/", ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:pk>/", ClientDetailView.as_view(), name="client_detail"),
    path("clients/<int:pk>/update/", ClientUpdateView.as_view(), name="client_update"),
    path("clients/<int:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    # Messages
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path(
        "messages/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"
    ),
    path(
        "messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
    # mailing
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailings/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path(
        "mailings/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"
    ),
    path(
        "mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"
    ),
    path("mailings/<int:pk>/send/", send_mailing_view, name="mailing_send"),
    # attempt
    path("attempts/", AttemptListView.as_view(), name="attempt_list"),
    path(
        "mailings/<int:pk>/attempts/",
        AttemptByMailingView.as_view(),
        name="attempt_list_by_mailing",
    ),
    path("stats/", StatsView.as_view(), name="stats"),
    path(
        "mailings/<int:pk>/toggle-enable/",
        mailing_toggle_enable,
        name="mailing_toggle_enable",
    ),
]
