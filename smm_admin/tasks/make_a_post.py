from celery import shared_task

from .notify_user import notify_user


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


def make_a_post(post, services=None):
    post.status = post.IN_PROGRESS
    post.save()

    if services is None:
        services = post.account.services.all()

    results = []

    for service in services:
        results.append(service.service.make_a_post(post=post))

    if all([not r.ok for r in results]):
        post.status = post.FAILED
    elif any([not r.ok for r in results]):
        post.status = post.PARTIALLY_FAILED
    else:
        post.status = post.OK

    post.save()

    notify_user(
        post.account.telegram_id,
        _get_result_text(post, results),
    )

    return post


@shared_task
def make_a_post_task(post_id, services=None):
    from django.apps import apps
    Post = apps.get_model('smm_admin', 'Post')
    post = Post.get(post_id)

    make_a_post(post, services)
