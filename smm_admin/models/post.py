import uuid

from django.db import models
from django.urls import reverse
from django.conf import settings

from easy_thumbnails.fields import ThumbnailerImageField


def generate_token():
    return str(uuid.uuid4()).replace('-', '')


class Post(models.Model):
    PARTIALLY_FAILED, FAILED, IN_PROGRESS, NOT_READY, READY, OK, DELETED = range(7)
    STATUSES = (
        (PARTIALLY_FAILED, 'Partially Failed'),
        (FAILED, 'Failed'),
        (IN_PROGRESS, 'In Progress'),
        (NOT_READY, 'Not Ready'),
        (READY, 'Ready'),
        (OK, 'OK'),
        (DELETED, 'Deleted'),
    )

    token = models.CharField(
        max_length=32,
        default=generate_token,
        blank=True,
        unique=True,
    )

    status = models.PositiveSmallIntegerField(
        choices=STATUSES,
        default=NOT_READY,
    )

    account = models.ForeignKey(
        'smm_admin.Account',
        on_delete=models.CASCADE,
    )

    schedule = models.DateTimeField(
        null=True,
        blank=True,
    )

    old_work = ThumbnailerImageField(
        null=True,
        blank=True,
    )
    new_work = ThumbnailerImageField(
        null=True,
        blank=True,
    )

    rendered_image = ThumbnailerImageField(
        null=True,
        blank=True,
    )

    artstation = models.CharField(
        max_length=256,
    )

    instagram = models.CharField(
        max_length=256,
        default='',
        blank=True,
    )

    old_work_year = models.PositiveSmallIntegerField()
    new_work_year = models.PositiveSmallIntegerField()

    old_work_url = models.CharField(max_length=4096, default='', blank=True)
    new_work_url = models.CharField(max_length=4096, default='', blank=True)

    name = models.CharField(max_length=255)

    text_en = models.TextField(
        default='',
        blank=True,
    )
    text_ru = models.TextField(
        default='',
        blank=True,
    )

    tags = models.TextField(
        default='',
        blank=True,
    )

    canvas_json = models.TextField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return '{} for {}'.format(
            self.account,
            self.name,
        )

    def save(self, **kwargs):
        if self.status in (self.READY, self.NOT_READY):
            if self.rendered_image and self.schedule:
                self.status = self.READY
            else:
                self.status = self.NOT_READY
        return super().save(**kwargs)

    @classmethod
    def get(cls, _id, values=False):
        obj = cls.objects.select_related(
            'account',
        )
        if values:
            obj = obj.values()

        obj = obj.get(id=_id)
        return obj

    @property
    def links_list(self):
        _list = [self.artstation]
        if self.instagram:
            _list.append(self.instagram)
        return _list

    def get_url(self):
        return '{}{}'.format(
            settings.DOMAIN_NAME,
            reverse('admin:smm_admin_post_change', args=[self.id]),
        )
