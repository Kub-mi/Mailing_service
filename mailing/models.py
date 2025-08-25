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