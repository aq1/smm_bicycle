from django.conf import settings

import facebook

from .base import Service


class FacebookService(Service):

    @property
    def data_format(self):
        return {
            'facebook_token',
            'facebook_group_id',
            'facebook_group_name',
        }

    @property
    def url(self):
        return 'https://facebook.com/{}'.format(self.model.data['facebook_group_id'])

    @property
    def url_title(self):
        return self.model.data['facebook_group_name']

    @property
    def login_url(self):
        return facebook.GraphAPI().get_auth_url(
            settings.FB_CLIENT_ID,
            settings.FB_REDIRECT_URI,
            ['manage_pages', 'publish_pages'],
        )

    def _get_post_link(self, result):
        return 'https://facebook.com/{}'.format(result['post_id'])

    def _get_caption(self):
        return '{}\n\n{}\n\n{}'.format(
            self.post.name,
            '\n'.join(map(str, self.post.links_list)),
            self.post.tags,
        )

    def _make_a_post(self):

        if not self.model.data['facebook_token']:
            return self.result.error('Need facebook token to make a post')

        graph = facebook.GraphAPI(
            access_token=self.model.data['facebook_token'],
            version='3.1',
        )

        try:
            accounts = graph.get_object('me/accounts')['data']
        except (facebook.GraphAPIError, KeyError) as e:
            return self.result.error('Failed to get page access token', str(e))

        access_token = None
        for acc in accounts:
            if acc['id'] == self.model.data['facebook_group_id']:
                access_token = acc['access_token']
                break

        if not access_token:
            return self.result.error('Failed to get page access token')

        graph = facebook.GraphAPI(
            access_token=access_token,
            version='3.1',
        )

        try:
            fb_post = graph.put_photo(
                self.post.rendered_image,
                message=self._get_caption(),
            )
        except facebook.GraphAPIError as e:
            return self.result.error(str(e))

        return self.result.success(
            self._get_post_link(fb_post),
            fb_post,
        )
