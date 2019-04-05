import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django import http
from django import views

from smm_admin import tasks
from smm_admin.models import (
    Post,
    Link,
)


class PostView(LoginRequiredMixin, views.View):

    @staticmethod
    def _clean_tags(tags):
        tags = map(str.strip, tags.split())
        return ' '.join([
            tag
            if tag.startswith('#')
            else '#{}'.format(tag)
            for tag in tags
        ])

    @staticmethod
    def get(request):
        return render(request, 'smm_admin/posts/new_post.html')

    def post(self, request):
        data = json.loads(request.body)

        try:
            post_data = dict(
                account_id=request.user.id,
                name_en=data['name_en'],
                name_ru=data.get('name_ru', ''),
                old_work_year=data['old_work']['year'],
                new_work_year=data['new_work']['year'],
                old_work_url=data['old_work'].get('url', ''),
                new_work_url=data['new_work'].get('url', ''),
                text_en=data.get('text_en', ''),
                text_ru=data.get('text_ru', ''),
                tags=self._clean_tags(data['tags']),
                schedule=data.get('schedule'),
            )
        except KeyError:
            return http.HttpResponse(status=400)

        with transaction.atomic():
            try:
                _post = Post.objects.create(**post_data)
            except IntegrityError:
                return http.HttpResponse(status=400)

            links = []
            for link in data['links']:
                if not link['value']:
                    continue

                if not link['value'].startswith('http'):
                    link['value'] = 'http://{}'.format(link['value'])

                links.append(Link(
                    post_id=_post.id,
                    url=link['value'],
                ))

            try:
                Link.objects.bulk_create(links)
            except IntegrityError:
                return http.HttpResponse(status=400)

        if _post.old_work_url or _post.new_work_url:
            tasks.download_image.delay('Post', _post.id)

        return http.JsonResponse(
            {'post_id': _post.id},
            status=201,
        )


@require_http_methods(['POST'])
@login_required
def post_file_upload(request, post_id):
    files = request.FILES
    if not files:
        return http.HttpResponse(status=400)

    old_work = files.get('old_work')
    new_work = files.get('new_work')
    if not (old_work or new_work):
        return http.HttpResponse(status=400)

    try:
        updated = Post.objects.filter(
            id=post_id,
            account_id=request.user.id,
        ).update(
            old_work=old_work,
            new_work=new_work,
        )
    except IntegrityError:
        return http.HttpResponse(status=400)

    if not updated:
        return http.HttpResponse(status=400)

    return http.HttpResponse(status=201)
