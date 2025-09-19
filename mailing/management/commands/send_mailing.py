from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from mailing.models import Mailing
from mailing.services import send_mailing


class Command(BaseCommand):
    help = "Отправка рассылок: по id или всех, чей период активен сейчас."

    def add_arguments(self, parser):
        parser.add_argument("--id", type=int, help="ID конкретной рассылки")
        parser.add_argument(
            "--due",
            action="store_true",
            help="Отправить все рассылки, у которых сейчас активное окно",
        )

    def handle(self, *args, **options):
        if options["id"]:
            mailing = Mailing.objects.filter(pk=options["id"]).first()
            if not mailing:
                raise CommandError("Рассылка с таким ID не найдена.")
            ok, total = send_mailing(mailing)
            self.stdout.write(
                self.style.SUCCESS(f"[{mailing.pk}] Отправлено {ok} из {total}")
            )
            return

        if options["due"]:
            now = timezone.now()
            qs = Mailing.objects.filter(start_at__lte=now, finish_at__gte=now)
            total_sent = 0
            total_msgs = 0
            for m in qs:
                ok, total = send_mailing(m)
                total_sent += ok
                total_msgs += total
                self.stdout.write(
                    self.style.SUCCESS(f"[{m.pk}] Отправлено {ok} из {total}")
                )
            self.stdout.write(
                self.style.SUCCESS(f"ИТОГО: {total_sent} из {total_msgs}")
            )
            return

        raise CommandError("Укажи --id <ID> или --due")
