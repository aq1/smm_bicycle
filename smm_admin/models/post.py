import uuid

from django.db import models
from django.urls import reverse
from django.conf import settings

from easy_thumbnails.fields import ThumbnailerImageField


def generate_token():
    return str(uuid.uuid4()).replace('-', '')


class Post(models.Model):
    FAILED, IN_PROGRESS, NOT_READY, READY, OK, DELETED = range(6)
    STATUSES = (
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
        blank=True,
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

    text_en = models.TextField()
    text_ru = models.TextField(
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
        if self.status == self.NOT_READY:
            if self.rendered_image and self.schedule:
                self.status = self.READY
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
    def ok(self):
        return all((r.ok for r in self.results.all()))

    def get_url(self):
        return '{}{}'.format(
            settings.DOMAIN_NAME,
            reverse('admin:smm_admin_post_change', args=[self.id]),
        )
