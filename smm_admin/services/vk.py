from django.urls import reverse

import requests

from .base import Service


class VkService(Service):
    _URL = 'https://api.vk.com/method/{}'

    @property
    def data_format(self):
        return {
            'vk_token',
            'vk_group_name',
            'vk_group_screen_name',
            'vk_group_id',
        }

    @property
    def url(self):
        return 'https://vk.com/{}'.format(self.model.data['vk_group_screen_name'])

    @property
    def url_title(self):
        return self.model.data['vk_group_name']

    @property
    def login_url(self):
        return reverse('vk_auth')

    def api_call(self, method, api_method, data=None, params=None, as_json=True):
        r = getattr(requests, method)
        data = data or {}
        params = params or {}
        params['access_token'] = self.model.data['vk_token']
        params['v'] = '5.92'
        response = r(self._URL.format(api_method), data=data, params=params)
        if as_json:
            return response.json()

    def _get_caption(self):
        return '{}\n{}\n\n{}\n\n{}'.format(
            self.post.name,
            '\n'.join(map(str, self.post.links_list)),
            self.post.text_ru or self.post.text_en,
            self.post.tags,
        )

    def _get_post_link(self, result):
        return 'https://vk.com/club{group}?w=wall-{group}_{post_id}'.format(
            group=self.model.data['vk_group_id'],
            post_id=result['response']['post_id']
        )

    def _make_a_post(self):

        owner_id = '-{}'.format(self.model.data['vk_group_id'])

        image_upload_server = self.api_call(
            'get',
            'photos.getWallUploadServer',
            params={'group_id': self.model.data['vk_group_id']}
        )
        if image_upload_server.get('error'):
            return self.result.error(image_upload_server['error'].get('error_msg'), image_upload_server)

        try:
            photo = requests.post(
                image_upload_server['response']['upload_url'],
                files={'file': self.post.rendered_image.file},
            )
        except requests.HTTPError as e:
            return self.result.error('Failed to upload the photo', str(e))

        photo = photo.json()

        response = self.api_call(
            'post',
            'photos.saveWallPhoto',
            data={
                'group_id': self.model.data['vk_group_id'],
                'hash': photo['hash'],
                'photo': photo['photo'],
                'server': photo['server'],
            }
        )

        if response.get('error'):
            return self.result.error(response['error'].get('error_msg'), response)

        photo = response['response'][0]
        response = self.api_call(
            'post',
            'wall.post',
            data={
                'from_group': 1,
                'owner_id': owner_id,
                'message': self._get_caption(),
                'attachments': ['photo{}_{}'.format(photo['owner_id'], photo['id'])],
            }
        )

        if response.get('error'):
            return self.result.error(response['error'].get('error_msg', ''), response)

        return self.result.success(
            self._get_post_link(response),
            response,
        )
