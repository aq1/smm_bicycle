from django import http
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required

import tweepy

from smm_admin.models import Service
from smm_admin.services import TWITTER


_SESSION_KEY = 'twitter_token'


@login_required
def twitter_auth(request):
    if request.GET.get('denied'):
        return redirect(reverse('account'))

    auth = tweepy.OAuthHandler(
        settings.TWITTER_CONSUMER_KEY,
        settings.TWITTER_CONSUMER_SECRET,
        settings.TWITTER_REDIRECT_URI,
    )

    if request.GET.get('oauth_token') and request.GET.get('oauth_verifier'):
        try:
            auth.request_token = request.session[_SESSION_KEY]
            key, secret = auth.get_access_token(request.GET['oauth_verifier'])
            auth.set_access_token(key, secret)
            api = tweepy.API(auth)
            user = api.me()
        except (ValueError, KeyError, tweepy.TweepError) as e:
            return http.HttpResponse(status=400)

        Service.objects.create(
            account_id=request.user.id,
            type=TWITTER,
            data={
                'twitter_token_key': key,
                'twitter_token_secret': secret,
                'twitter_username': user.screen_name,
            },
        )
        return redirect(reverse('account'))

    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        return http.HttpResponse(status=400)

    request.session[_SESSION_KEY] = auth.request_token
    return redirect(redirect_url)
