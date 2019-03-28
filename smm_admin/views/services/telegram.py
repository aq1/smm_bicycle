from django import http
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from smm_admin.models import Service
from smm_admin.services import TELEGRAM


@require_http_methods(['POST'])
@login_required
def telegram_channel_form(request):
    try:
        channel_id = request.POST['telegram_channel']
        bot_token = request.POST['telegram_bot_token']
    except KeyError:
        return http.HttpResponse(status=400)

    try:
        Service.objects.create(
            account_id=request.user.id,
            type=TELEGRAM,
            data={
                'telegram_channel_id': channel_id,
                'telegram_token': bot_token,
            },
        )
    except IntegrityError:
        return http.HttpResponse(status=400)

    return redirect(reverse('account'))


@require_http_methods(['GET'])
@login_required
def telegram_auth(request):
    return render(request, 'smm_admin/services/telegram_auth.html')
