from django.templatetags.static import static
from django.core.exceptions import ValidationError

from smm_admin.models import (
    Post,
    PostResult,
)


class Service:

    def __init__(self, model):
        self.model = model
        self.post = None
        self.result = PostResult(service=self)

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.__class__.__name__[:len(self.__class__.__name__) - len('Service')]

    @property
    def data_format(self):
        return {}

    @property
    def logo_url(self):
        return static('smm_admin/img/{}_logo.png'.format(self.name.lower()))

    @property
    def url(self):
        raise NotImplementedError()

    @property
    def url_title(self):
        raise NotImplementedError()

    @property
    def login_url(self):
        raise NotImplementedError()

    def _get_caption(self):
        raise NotImplementedError()

    def _get_post_link(self, result):
        raise NotImplementedError()

    def _make_a_post(self):
        raise NotImplementedError()

    def _clean(self):
        pass

    def clean(self):
        if self.data_format != self.model.data.keys():
            raise ValidationError('Wrong data format. Expected {} keys'.format(self.data_format))

        self._clean()

    def make_a_post(self, post_id=None, post=None):
        if post_id and not post:
            post = Post.get(post_id)

        self.result.post = post
        self.result.post_id_raw = post.id

        if not post.rendered_image:
            return self.result.error('Need a rendered picture to make a post')

        self.post = post
        try:
            self.post.rendered_image.file.seek(0)
        except ValueError:
            # if a service decide to close a file (I've never asked for this)
            self.post.rendered_image.file.open()

        result = self._make_a_post()
        result.save()
        return result
