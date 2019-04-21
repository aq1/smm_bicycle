from urllib.parse import urlparse

from django.conf import settings
from django.core.files import uploadedfile

import requests
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


def get_image_file(url):
    r = requests.get(url)
    return uploadedfile.SimpleUploadedFile(
        urlparse(url).path.split('/')[-1],
        r.content,
        r.headers['Content-Type'],
    )


@shared_task
def download_image(model, post_id):
    from django.apps import apps
    model = apps.get_model('smm_admin', model)

    try:
        post = model.objects.get(id=post_id)
    except model.DoesNotExist:
        return False

    if not (post.old_work_url or post.new_work_url):
        raise ValueError('Expected at least one url')

    if post.old_work_url and not post.old_work:
        post.old_work = get_image_file(post.old_work_url)

    if post.new_work_url and not post.new_work:
        post.new_work = get_image_file(post.new_work_url)

    post.save()


@shared_task
def make_posts():

    from django.apps import apps
    model = apps.get_model('smm_admin', 'Post')

    posts = model.objects.filter()
