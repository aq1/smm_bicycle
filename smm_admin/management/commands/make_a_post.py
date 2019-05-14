from django.core.management.base import BaseCommand

from smm_admin.models import Post
from smm_admin.tasks.make_a_post import (
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
        try:
            post = Post.objects.get(id=options['post_id'])
        except Post.DoesNotExist:
            self.stderr.write(self.style.ERROR('Post not found'))
            return
        make_a_post(post)
        self.stdout.write(self.style.SUCCESS('Done.\n'))
