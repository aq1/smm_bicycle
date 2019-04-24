from django.urls import reverse

import telegram

from .base import Service


class TelegramService(Service):

    @property
    def data_format(self):
        return {
            'telegram_channel_id',
            'telegram_token',
        }

    @property
    def url(self):
        return 'https://t.me/{}'.format(self.model.data['telegram_channel_id'])

    @property
    def url_title(self):
        return '@{}'.format(self.model.data['telegram_channel_id'])

    @property
    def login_url(self):
        return reverse('telegram_auth')

    def _clean(self):
        if self.model.data['telegram_channel_id'].startswith('@'):
            self.model.data['telegram_channel_id'] = self.model.data['telegram_channel_id'][1:]

    def _get_post_link(self, result):
        return result.link

    def _get_caption(self):
        links = ' / '.join([
            link.for_telegram()
            for link in self.post.links_list
        ])
        return '<b>{}</b> {}'.format(self.post.name, links)

    def _make_a_post(self):
        kwargs = dict(
            chat_id='@{}'.format(self.model.data['telegram_channel_id']),
            photo=self.post.rendered_image.open(),
            caption=self._get_caption(),
            parse_mode='HTML',
            disable_notification=True,
            disable_web_page_preview=True,
        )
        try:
            message = telegram.Bot(token=self.model.data['telegram_token']).send_photo(**kwargs)
        except telegram.error.TelegramError as e:
            return self.result.error(str(e))

        return self.result.success(
            self._get_post_link(message),
            message,
        )
