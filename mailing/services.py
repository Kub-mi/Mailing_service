from django.core.mail import EmailMessage
from django.utils import timezone

from .models import Mailing


def send_mailing(mailing: Mailing) -> tuple[int, int]:
    """
    Отправляет письма всем получателям рассылки.
    Возвращает кортеж (успешно, всего).
    """
    sent_ok = 0
    total = mailing.recipients.count()

    # помечаем как «Запущена» при первой отправке
    if mailing.status == Mailing.STATUS_CREATED:
        mailing.status = Mailing.STATUS_RUNNING
        mailing.save(update_fields=["status"])

    for r in mailing.recipients.all():
        try:
            email = EmailMessage(
                subject=mailing.message.subject,
                body=mailing.message.body,
                to=[r.email],
            )
            # send() возвращает 1 при успехе, 0 — при фейле
            sent_ok += int(bool(email.send(fail_silently=False)))
        except Exception:

            pass

    # если окно уже прошло — закрываем рассылку
    if mailing.finish_at <= timezone.now():
        mailing.status = Mailing.STATUS_FINISHED
        mailing.save(update_fields=["status"])

    return sent_ok, total
