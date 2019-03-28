from django.core.management.base import BaseCommand

from smm_admin.tasks import (
    make_a_post,
)


class Command(BaseCommand):
    help = 'Make a post'

    def add_arguments(self, parser):
        parser.add_argument(
            'post_id',
            type=int,
            help='Post ID in database',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Working...\n'))
        make_a_post(options['post_id'])
        self.stdout.write(self.style.SUCCESS('Done.\n'))
