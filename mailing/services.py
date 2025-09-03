from django.core.mail import EmailMessage
from django.utils import timezone

from .models import Mailing, Attempt


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


def send_mailing(mailing: Mailing) -> tuple[int, int]:
    sent_ok = 0
    recipients = mailing.recipients.all()
    total = recipients.count()

    if mailing.status == Mailing.STATUS_CREATED:
        mailing.status = Mailing.STATUS_RUNNING
        mailing.save(update_fields=["status"])

    for r in recipients:
        try:
            email = EmailMessage(
                subject=mailing.message.subject,
                body=mailing.message.body,
                to=[r.email],
            )
            ok = bool(email.send(fail_silently=False))
            if ok:
                sent_ok += 1
                Attempt.objects.create(
                    mailing=mailing,
                    client=r,
                    status=Attempt.STATUS_SUCCESS,
                    server_response="OK",
                )
            else:
                Attempt.objects.create(
                    mailing=mailing,
                    client=r,
                    status=Attempt.STATUS_FAILED,
                    server_response="send() returned 0",
                )
        except Exception as e:
            Attempt.objects.create(
                mailing=mailing,
                client=r,
                status=Attempt.STATUS_FAILED,
                server_response=str(e),
            )

    if mailing.finish_at <= timezone.now():
        mailing.status = Mailing.STATUS_FINISHED
        mailing.save(update_fields=["status"])

    return sent_ok, total
