from django.conf import settings
from django.urls import reverse

import tweepy
from easy_thumbnails.files import get_thumbnailer

from .base import Service


class TwitterService(Service):

    @property
    def data_format(self):
        return {
            'twitter_token_key',
            'twitter_token_secret',
            'twitter_username',
        }

    @property
    def url(self):
        return 'https://twitter.com/{}'.format(self.model.data['twitter_username'])

    @property
    def url_title(self):
        return '@{}'.format(self.model.data['twitter_username'])

    @property
    def login_url(self):
        return reverse('twitter_auth')

    def _get_post_link(self, result):
        return 'https://twitter.com/{}/status/{}'.format(
            result.user.screen_name,
            result.id_str,
        )

    def _get_caption(self):
        return '{}\n\n{}'.format(
            self.post.name,
            '\n'.join(self.post.links_list),
        )

    def _make_a_post(self):

        auth = tweepy.OAuthHandler(
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET,
            settings.TWITTER_REDIRECT_URI,
        )
        auth.set_access_token(
            self.model.data['twitter_token_key'],
            self.model.data['twitter_token_secret'],
        )
        api = tweepy.API(auth)

        try:
            api.verify_credentials()
        except tweepy.TweepError as e:
            return self.result.error(str(e))

        try:
            result = api.update_with_media(
                filename=self.post.rendered_image.name,
                status=self._get_caption(),
                file=get_thumbnailer(self.post.rendered_image)['1920'].file,
            )
        except tweepy.TweepError as e:
            return self.result.error(str(e))

        return self.result.success(
            text=self._get_post_link(result),
            raw=result._json,
        )
