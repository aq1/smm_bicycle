from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@require_http_methods(['GET'])
@login_required
def edit_post(request, post_id):
    return render(request, 'smm_admin/posts/edit_post.html', {'post_id': post_id})
