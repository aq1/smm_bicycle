from django.core.management.base import BaseCommand
from django.utils import timezone

from smm_admin.models import Post
from smm_admin.tasks.make_a_post import make_a_post


class Command(BaseCommand):
    """
    Something like
    */5 * * * * /_projects/smm_bicycle/.env/bin/python /_projects/smm_bicycle/manage.py make_posts
    """
    help = 'Make posts by a schedule'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Working...\n'))

        posts = Post.objects.filter(
            status=Post.READY,
            schedule__lte=timezone.now(),
        ).select_related(
            'account',
        )

        for post in posts:
            make_a_post(post)
            if post.status == post.OK:
                self.stdout.write(self.style.SUCCESS('Posted {}\n'.format(post.name)))
            else:
                self.stderr.write(self.style.ERROR('Failed {}\n'.format(post.name)))

        self.stdout.write(self.style.SUCCESS('Done.\n'))
