import binascii
import base64
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, render
from django import http
from django import views

from rest_framework import serializers

from smm_admin import tasks
from smm_admin.models import (
    Post,
    Link,
)


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        exclude = (
            'post',
        )
        depth = 1


class PostSerializer(serializers.ModelSerializer):
    links = LinkSerializer(read_only=True, many=True)

    class Meta:
        model = Post
        exclude = (
            'id',
        )
        depth = 1


@login_required
@require_http_methods(['GET'])
def post(request, post_id):
    return http.JsonResponse(
        PostSerializer(
            instance=get_object_or_404(
                Post,
                id=post_id,
                account__user_id=request.user.id,
            )
        ).data
    )


@require_http_methods(['GET'])
@login_required
def post_view(request, post_id):
    try:
        _post = Post.objects.prefetch_related('links').get(
            id=post_id,
            account_id=request.user.id,
        )
    except Post.DoesNotExist:
        return http.HttpResponse(status=400)

    return render(request, 'smm_admin/post.html', {'post': _post})


@login_required
@require_http_methods(['POST'])
def save_canvas(request, post_id):
    try:
        json.loads(request.body)
    except (ValueError, json.JSONDecodeError):
        return http.HttpResponse(status=400)

    updated = Post.objects.filter(
        id=post_id,
        account__user_id=request.user.id,
    ).update(
        canvas_json=request.body.decode('utf8'),
    )
    if updated == 0:
        return http.HttpResponse(status=404)

    return http.HttpResponse(status=201)


@login_required
@require_http_methods(['POST'])
def save_render(request, post_id):
    if not request.GET.get('f'):
        return http.HttpResponse(status=400)

    try:
        _post = Post.objects.get(
            id=post_id,
            account__user_id=request.user.id,
        )
    except Post.DoesNotExist:
        return http.HttpResponse(status=404)

    try:
        _post.rendered_image.save(
            request.GET['f'],
            ContentFile(base64.b64decode(request.body.decode('utf8').split(',')[1])),
        )
    except (binascii.Error, TypeError, IndexError, ValueError):
        return http.HttpResponse(status=400)
    return http.JsonResponse({'url': _post.rendered_image.url}, status=201)


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
        return render(request, 'smm_admin/new_post.html')

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
