from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from smm_admin.tasks.notify_user import (
    notify_user,
)


class Command(BaseCommand):
    help = 'Make posts by a schedule'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Working...\n'))
        notify_user(
            get_user_model().objects.get(is_superuser=True).account.telegram_id,
            'Testing schedule',
        )
        self.stdout.write(self.style.SUCCESS('Done.\n'))
