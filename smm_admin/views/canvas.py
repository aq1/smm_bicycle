import binascii
import base64
import json

from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import render
from django import http

from smm_admin.models import (
    Post,
)


@login_required
def canvas(request, post_id):
    return render(
        request,
        'smm_admin/canvas.html',
        context={'post_id': post_id},
    )


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
