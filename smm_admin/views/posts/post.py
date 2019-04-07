from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404

from smm_admin.models import (
    Post,
)


@require_http_methods(['GET'])
def post_view(request, post_id=None, token=None):
    if token:
        _post = get_object_or_404(Post, token=token)
    else:
        _post = get_object_or_404(Post, id=post_id, account_id=post_id)

    return render(
        request,
        'smm_admin/posts/post.html',
        {
            'post': _post,
            'by_token': token and request.user.is_anonymous,
        },
    )
