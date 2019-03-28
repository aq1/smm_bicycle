from urllib.parse import urlparse

from django.db import models


class Link(models.Model):
    post = models.ForeignKey(
        'smm_admin.Post',
        on_delete=models.CASCADE,
        related_name='links',
    )

    url = models.CharField(max_length=255)

    def __str__(self):
        return '{} {}'.format(self.host, self.url)

    @property
    def host(self):
        url = urlparse(self.url).netloc
        if url.startswith('www.'):
            url = url[4:]
        return url.split('.')[0]

    @classmethod
    def for_post(cls, post_id):
        return list(cls.objects.select_related(
            'type',
        ).filter(
            post_id=post_id,
        ))

    def for_telegram(self):
        return '<a href="{}">{}</a>'.format(
            self.url,
            self.host,
        )
