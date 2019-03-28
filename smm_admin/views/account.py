from django import http
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.views.decorators.http import require_http_methods
from django.core.validators import validate_email
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from smm_admin.services import SERVICES


@login_required
@require_http_methods(['GET'])
def account(request):
    return render(
        request,
        'smm_admin/account.html',
        {
            'user': request.user,
            'services': [s(None) for s in SERVICES],
        },
    )


@login_required
@require_http_methods(['POST'])
def account_post(request):
    # FIXME: This is bad, I really should not waste time on things that were done so many times before.

    try:
        username, telegram_id = request.POST['username'], request.POST['telegram_id']
    except KeyError:
        return http.HttpResponse(status=400)

    logo = request.FILES.get('logo')

    errors = {}

    try:
        validate_email(username)
    except ValidationError:
        errors['email'] = 'Invalid Email'

    try:
        telegram_id = int(telegram_id)
        if telegram_id <= 0:
            raise ValueError
    except ValueError:
        errors['telegram'] = 'Invalid Telegram ID. Expected positive integer'

    # Do I look like I care?
    request.user.username = username
    request.user.email = username
    request.user.account.telegram_id = telegram_id
    if logo:
        request.user.account.logo = logo

    if errors:
        return render(
            request,
            'smm_admin/account.html',
            {
                'user': request.user,
                'errors': errors,
            },
        )

    try:
        request.user.save()
        request.user.account.save()
    except IntegrityError:
        return http.HttpResponse(status=400)

    return redirect(reverse('account'))
