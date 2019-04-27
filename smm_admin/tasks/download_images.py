from urllib.parse import urlparse

from django.core.files import uploadedfile

import requests
from celery import shared_task


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
