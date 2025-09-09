from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = "Создаёт группу 'Менеджеры' и назначает ей права"

    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name="Менеджеры")

        perm_codenames = [
            "view_all_clients",
            "view_all_messages",
            "view_all_mailings",
            "disable_mailings",
            "view_user_list",
            "block_users",
        ]

        added = 0
        for codename in perm_codenames:
            try:
                perm = Permission.objects.get(codename=codename)
                group.permissions.add(perm)
                added += 1
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Права {codename} не найдены (миграции применены?)"))

        self.stdout.write(self.style.SUCCESS(f"Группа 'Менеджеры' готова, назначено прав: {added}"))
