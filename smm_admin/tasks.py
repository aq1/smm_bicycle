from django.conf import settings

import telegram

from celery import shared_task


@shared_task
def notify_user(telegram_id, text):
    return telegram.Bot(token=settings.TELEGRAM_TOKEN).send_message(
        chat_id=telegram_id,
        text=text,
        parse_mode='HTML',
        disable_web_page_preview=True,
    )


def _get_result_text(post, results):
    text = []
    for result in results:
        if result.ok:
            status = '✔'
            status_text = '<a href="{}">link</a>'.format(result.text)
        else:
            status = '❗'
            status_text = result.text

        text.append('<b>{}</b> {} {}'.format(
            status,
            result.service,
            status_text,
        ))

    return 'Post: {} <a href="{}">{}</a>\n{}'.format(
        post.id,
        post.get_url(),
        post,
        '\n'.join(text),
    )


@shared_task
def make_a_post(post_id, services=None):
    from django.apps import apps

    Post = apps.get_model('smm_admin', 'Post')

    post = Post.get(post_id)

    if services is None:
        services = post.account.services.all()

    results = []

    for service in services:
        results.append(service.service.make_a_post(post=post))

    notify_user(
        post.account.telegram_id,
        _get_result_text(post, results),
    )


@shared_task
def download_image(suggested_post_id):
    from django.apps import apps
    PostSuggestion = apps.get_model('smm_admin', 'PostSuggestion')

    try:
        post = PostSuggestion.get(id=suggested_post_id)
    except PostSuggestion.DoesNotExist:
        return False

    if not post.old_work and post.old_work_url:
        pass

    if not post.new_work and post.new_work_url:
        pass

    post.save()
