import urllib.parse

from django import http
from django.conf import settings
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

import requests

from smm_admin.models import Service
from smm_admin.services import VK

VK_URL = (
    'https://oauth.vk.com/authorize'
    '?client_id={}'
    '&display=page'
    '&redirect_uri=https://oauth.vk.com/blank.html'
    '&scope={}'
    '&response_type=token'
    '&v=5.92'
).format(
    settings.VK_CLIENT_ID,
    str(4 + 8192 + 65536 + 262144),
)


def get_vk_token(code):
    response = requests.get(
        'https://oauth.vk.com/access_token',
        params={
            'client_id': settings.VK_CLIENT_ID,
            'client_secret': settings.VK_CLIENT_SECRET,
            'redirect_uri': settings.VK_REDIRECT_URI,
            'code': code,
        }
    )

    if response.status_code != 200:
        raise ValueError

    data = response.json()
    return data['access_token'], data['user_id']


@login_required
@require_http_methods(['GET'])
def vk_groups(request):
    response = requests.post(
        'https://api.vk.com/method/groups.get',
        data={
            'filter': 'moder',
            'extended': 1,
            'fields': 'id,name,screen_name,photo_50',
        },
        params={
            'v': '5.92',
            'access_token': request.session['vk_token'],
        }
    )

    if response.status_code != 200:
        return http.HttpResponse(status=400)

    try:
        data = response.json()['response']['items']
    except (ValueError, KeyError):
        return http.HttpResponse(status=400)

    request.session['vk_groups'] = data
    return render(request, 'smm_admin/services/vk_group_select.html', {'groups': data})


@login_required
@require_http_methods(['POST'])
def vk_group_selected(request):
    try:
        group_index = request.POST['group']
    except (KeyError, ValueError):
        return http.HttpResponse(status=400)

    try:
        group = request.session['vk_groups'][int(group_index)]
    except (IndexError, ValueError):
        return http.HttpResponse(status=400)

    del request.session['vk_groups']

    try:
        Service.objects.create(
            account_id=request.user.id,
            type=VK,
            data={
                'vk_token': request.session.pop('vk_token'),
                'vk_group_id': group['id'],
                'vk_group_screen_name': group['screen_name'],
                'vk_group_name': group['name'],
            }
        )
    except (KeyError, IntegrityError):
        return http.HttpResponse(status=400)

    return redirect(reverse('account'))


@require_http_methods(['GET'])
@login_required
def vk_auth(request):
    return render(request, 'smm_admin/services/vk_auth.html', {'url': VK_URL})


@require_http_methods(['POST'])
@login_required
def vk_auth_post(request):
    error, token = None, None
    if not request.POST.get('vk_url'):
        error = 'Need url'

    url = urllib.parse.urlparse(request.POST.get('vk_url'))
    if url.hostname != 'oauth.vk.com':
        error = 'Bad URL'

    if url.fragment:
        parameters = [each.split('=') for each in url.fragment.split('&')]
        for name, value in parameters:
            if name == 'access_token':
                token = value
                break

    if not token:
        error = 'Bad URL'

    if error:
        return render(
            request,
            'smm_admin/services/vk_auth.html',
            {'url': VK_URL, 'error': error},
        )

    request.session['vk_token'] = token
    return redirect('vk_groups')
