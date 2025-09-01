from django.db import models
from django.conf import settings


class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец',related_name='clients')

    class Meta:
        verbose_name = 'получатель'
        verbose_name_plural = "получатели"
        permissions =[
            ('view_all_clients', 'Can view all clients (manager)'),
        ]

    def __str__(self):
        return f'{self.full_name} <{self.email}>'


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='messages', verbose_name='Владелец')

    class Meta:
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'
        permissions = [
            ('view_all_messages', 'Can view all messages (manager)'),
        ]

    def __str__(self):
        return self.subject


class Mailing (models.Model):
    STATUS_CREATED = "Создана"
    STATUS_RUNNING = "Запущена"
    STATUS_FINISHED = "Завершена"
    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_RUNNING, "Запущена"),
        (STATUS_FINISHED, "Завершена"),
    ]

    start_at = models.DateTimeField(verbose_name='Дата/время первой отправки')
    finish_at = models.DateTimeField(verbose_name='Дата/время окончания отправок')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_CREATED, verbose_name='Статус')
    message = models.ForeignKey('mailing.Message', on_delete=models.CASCADE, verbose_name='Сообщение')
    recipients = models.ManyToManyField('mailing.Client', blank=True, related_name='mailings', verbose_name='Получатели')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец")

    class Meta:
        verbose_name = "рассылка"
        verbose_name_plural = "рассылки"
        permissions = [
            ("view_all_mailings", "Can view all mailings (manager)"),
        ]

    def __str__(self):
        return f'Рассылка #{self.pk} - {self.status}'
