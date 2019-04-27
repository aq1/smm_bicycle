from django.shortcuts import render, get_object_or_404

from smm_admin.models import Account


def post_suggest_view(request, account_id):
    account = get_object_or_404(Account, user_id=account_id)
    return render(
        request,
        'smm_admin/posts/edit_post.html',
        {'account': account},
    )
