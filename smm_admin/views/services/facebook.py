from django import http
from django.db import IntegrityError
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.conf import settings
from django.urls import reverse

import requests
import facebook

from smm_admin.models import Service
from smm_admin.services import FACEBOOK


@login_required
@require_http_methods(['GET'])
def fb_auth(request):
    if request.GET.get('error'):
        return redirect(reverse('account'))

    code = request.GET.get('code')
    if not code:
        return redirect(request.user.account.fb_login_url)

    response = requests.get(
        'https://graph.facebook.com/v3.2/oauth/access_token',
        params={
            'client_id': settings.FB_CLIENT_ID,
            'redirect_uri': settings.FB_REDIRECT_URI,
            'client_secret': settings.FB_CLIENT_SECRET,
            'code': code,
        }
    )

    if response.status_code != 200:
        return http.HttpResponse(status=400)

    request.session['facebook_token'] = response.json()['access_token']
    return redirect(reverse('fb_groups_select'))


@login_required
@require_http_methods(['GET'])
def fb_groups_select(request):
    graph = facebook.GraphAPI(request.session['facebook_token'])
    groups = graph.get_object(
        'me/accounts',
        fields='id,name,cover'
    )['data']

    request.session['fb_groups'] = groups
    return render(
        request,
        'smm_admin/services/fb_group_select.html',
        {'groups': groups},
    )


@login_required
@require_http_methods(['POST'])
def fb_group_selected(request):
    try:
        group_index = request.POST['group']
    except (KeyError, ValueError):
        return http.HttpResponse(status=400)

    try:
        group = request.session['fb_groups'][int(group_index)]
    except (IndexError, ValueError):
        return http.HttpResponse(status=400)

    del request.session['fb_groups']

    try:
        Service.objects.create(
            type=FACEBOOK,
            account_id=request.user.id,
            data={
                'facebook_token': request.session.get('facebook_token'),
                'facebook_group_id': group['id'],
                'facebook_group_name': group['name'],
            }
        )
    except (KeyError, IntegrityError):
        return http.HttpResponse(status=400)

    return redirect(reverse('account'))
