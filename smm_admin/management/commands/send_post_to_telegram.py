import urllib.parse

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

import telegram

from smm_admin.models import Post


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Working...\n'))

        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        now = timezone.now()

        posts_for_instagram = Post.objects.filter(
            status=Post.READY,
            schedule__gte=now.replace(hour=0, minute=0, second=0, microsecond=0),
            schedule__lte=now.replace(hour=23, minute=59, second=59, microsecond=999999),
        ).select_related(
            'account',
        )

        for post in posts_for_instagram:
            delimiter = '_' * 57
            links = [post.artstation]
            if post.instagram:
                instagram = urllib.parse.urlparse(post.instagram)
                links.insert(0, '@{}'.format(instagram.path.replace('/', '')))
            text = [post.name, '\n'.join(links), delimiter]

            if post.text_en:
                text += [post.text_en, delimiter]

            text.append(post.tags)

            bot.send_message(
                chat_id=post.account.telegram_id,
                text='\n'.join(text),
                disable_web_page_preview=True,
            )
            for photo, year in ((post.old_work, post.old_work_year), (post.new_work, post.new_work_year)):
                bot.send_photo(
                    chat_id=post.account.telegram_id,
                    photo=settings.HOST + photo.url,
                    caption=str(year),
                )

            self.stdout.write(self.style.SUCCESS('Sent {}.\n'.format(post.name)))

        self.stdout.write(self.style.SUCCESS('Done.\n'))
