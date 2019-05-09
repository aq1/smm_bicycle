from django.core.management.base import BaseCommand
from django.utils import timezone

from smm_admin.models import Post
from smm_admin.services import TELEGRAM
from smm_admin.tasks.make_a_post import make_a_post


class Command(BaseCommand):
    """
    Something like
    */5 * * * * /_projects/smm_bicycle/.env/bin/python /_projects/smm_bicycle/manage.py make_posts
    """
    help = 'Make posts by a schedule'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Working...\n'))

        now = timezone.now()

        posts_for_instagram = Post.objects.filter(
            status=Post.READY,
            schedule__lte=now + timezone.timedelta(minutes=15),
            schedule__gte=now + timezone.timedelta(minutes=10),
        ).select_related(
            'account',
        )

        for post in posts_for_instagram:
            telegram_service = post.account.services.filter(type=TELEGRAM).first().service
            for photo, year in ((post.old_work, post.old_work_year), (post.new_work, post.new_work_year)):
                telegram_service.send_photo(
                    chat_id=post.account.telegram_id,
                    photo=photo.open(),
                    caption=str(year),
                )
            telegram_service.send_message(
                chat_id=post.account.telegram_id,
                text=post.text_en,
            )

        posts = Post.objects.filter(
            status=Post.READY,
            schedule__lte=now
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
