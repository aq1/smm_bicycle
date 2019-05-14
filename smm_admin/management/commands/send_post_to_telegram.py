from django.core.management.base import BaseCommand
from django.utils import timezone

from smm_admin.models import Post
from smm_admin.services import TELEGRAM


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Working...\n'))

        now = timezone.now()
        posts_for_instagram = Post.objects.filter(
            status=Post.READY,
            schedule__gte=now.replace(hour=0, minute=0, second=0, microsecond=0),
            schedule__lte=now.replace(hour=23, minute=59, second=59, microsecond=999999),
        ).select_related(
            'account',
        )

        for post in posts_for_instagram:
            telegram_service = post.account.services.filter(type=TELEGRAM).first().service

            telegram_service.send_message(
                chat_id=post.account.telegram_id,
                text=post.name,
            )

            for photo, year in ((post.old_work, post.old_work_year), (post.new_work, post.new_work_year)):
                telegram_service.send_photo(
                    chat_id=post.account.telegram_id,
                    photo=photo.open(),
                    caption=str(year),
                )
            if post.text_en:
                telegram_service.send_message(
                    chat_id=post.account.telegram_id,
                    text=post.text_en,
                )
            links = [post.artstation]
            if post.instagram:
                links.append(post.instagram)
            telegram_service.send_message(
                chat_id=post.account.telegram_id,
                text='\n'.join(links),
            )
            self.stdout.write(self.style.SUCCESS('Sent {}.\n'.format(post.name)))

        self.stdout.write(self.style.SUCCESS('Done.\n'))
