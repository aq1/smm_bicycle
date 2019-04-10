from django import http
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404

from smm_admin.models import (
    Post,
)


@require_http_methods(['GET'])
def post_view(request, post_id=None, token=None):
    if token:
        _post = get_object_or_404(Post, token=token)
    elif not request.user.is_anonymous:
        _post = get_object_or_404(Post, id=post_id, account_id=request.user.id)
    else:
        return http.HttpResponse(status=404)

    return render(
        request,
        'smm_admin/posts/post.html',
        {
            'post': _post,
            'by_token': token and request.user.is_anonymous,
        },
    )
