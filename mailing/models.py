from django.db import models
from django.conf import settings


class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name="clients",
    )

    class Meta:
        verbose_name = "получатель"
        verbose_name_plural = "получатели"
        permissions = [
            ("view_all_clients", "Может просматривать всех клиентов"),
        ]
        ordering = ["-id"]

    def __str__(self):
        return f"{self.full_name} <{self.email}>"


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Владелец",
    )

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"
        permissions = [
            ("view_all_messages", "Может просматривать все сообщения"),
        ]

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    STATUS_CREATED = "Создана"
    STATUS_RUNNING = "Запущена"
    STATUS_FINISHED = "Завершена"
    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_RUNNING, "Запущена"),
        (STATUS_FINISHED, "Завершена"),
    ]

    start_at = models.DateTimeField(verbose_name="Дата/время первой отправки")
    finish_at = models.DateTimeField(verbose_name="Дата/время окончания отправок")
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name="Статус",
    )
    message = models.ForeignKey(
        "mailing.Message", on_delete=models.CASCADE, verbose_name="Сообщение"
    )
    recipients = models.ManyToManyField(
        "mailing.Client", blank=True, related_name="mailings", verbose_name="Получатели"
    )
    is_enabled = models.BooleanField(default=True, verbose_name="Включена")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец"
    )

    class Meta:
        verbose_name = "рассылка"
        verbose_name_plural = "рассылки"
        permissions = [
            ("view_all_mailings", "Может просматривать все рассылки"),
            ("disable_mailings", "Может отключать рассылки пользователей"),
        ]

    def __str__(self):
        return f"Рассылка #{self.pk} - {self.status}"


class Attempt(models.Model):
    STATUS_SUCCESS = "Успешно"
    STATUS_FAILED = "Не успешно"
    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Успешно"),
        (STATUS_FAILED, "Не успешно"),
    ]

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата/время попытки"
    )
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, verbose_name="Статус"
    )
    server_response = models.TextField(
        blank=True, verbose_name="Ответ почтового сервера"
    )

    mailing = models.ForeignKey(
        "mailing.Mailing",
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Рассылка",
    )
    # Поле клиента — не обязательно по ТЗ, но очень полезно для отчётов:
    client = models.ForeignKey(
        "mailing.Client",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attempts",
        verbose_name="Получатель",
    )

    class Meta:
        verbose_name = "попытка рассылки"
        verbose_name_plural = "попытки рассылок"
        ordering = ["-created_at"]
