from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django import http

from smm_admin.models import (
    Post,
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

    return render(request, 'smm_admin/posts/post.html', {'post': _post})
