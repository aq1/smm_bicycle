from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.postgres.fields import ArrayField


class Post(models.Model):
    IN_PROGRESS, NOT_READY, READY, OK, FAILED = range(5)
    STATUSES = (
        (IN_PROGRESS, 'In Progress'),
        (NOT_READY, 'Not Ready'),
        (READY, 'Ready'),
        (OK, 'OK'),
        (FAILED, 'Failed'),
    )

    status = models.PositiveSmallIntegerField(
        choices=STATUSES,
        default=NOT_READY,
    )

    suggested = models.BooleanField(
        default=False,
        blank=True,
    )

    account = models.ForeignKey(
        'smm_admin.Account',
        on_delete=models.CASCADE,
    )

    schedule = models.DateTimeField(
        null=True,
        blank=True,
    )

    old_work = models.ImageField(
        null=True,
        blank=True,
    )
    new_work = models.ImageField(
        null=True,
        blank=True,
    )

    rendered_image = models.ImageField(
        null=True,
        blank=True,
    )

    links = ArrayField(
        models.CharField(max_length=5000),
    )

    old_work_year = models.PositiveSmallIntegerField()
    new_work_year = models.PositiveSmallIntegerField()

    old_work_url = models.CharField(max_length=4096, default='', blank=True)
    new_work_url = models.CharField(max_length=4096, default='', blank=True)

    name_en = models.CharField(max_length=255)
    name_ru = models.CharField(
        max_length=255,
        default='',
        blank=True,
    )

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
            self.name_en,
        )

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
