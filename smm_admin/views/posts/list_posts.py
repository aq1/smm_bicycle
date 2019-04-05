from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@require_http_methods(['GET'])
@login_required
def list_posts(request):
    return render(
        request,
        'smm_admin/posts/list_posts.html',
    )
