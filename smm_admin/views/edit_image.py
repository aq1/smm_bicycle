from django.shortcuts import render

from django.contrib.auth.decorators import login_required


@login_required
def edit_image(request, post_id):
    return render(
        request,
        'smm_admin/edit_image.html',
        context={'post_id': post_id},
    )
