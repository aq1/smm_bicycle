from django.conf import settings

import telegram

from celery import shared_task


@shared_task
def notify_user(telegram_id, text):
    telegram.Bot(token=settings.TELEGRAM_TOKEN).send_message(
        chat_id=telegram_id,
        text=text,
        parse_mode='HTML',
        disable_web_page_preview=True,
    )
