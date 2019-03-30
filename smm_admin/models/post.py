from django.db import models
from django.urls import reverse
from django.conf import settings

from project import celery

from smm_admin import tasks


class Post(models.Model):

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
    tags = models.TextField()

    canvas_json = models.TextField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return '{} for {}'.format(
            self.account,
            self.name_en,
        )

    def save(self, **kwargs):
        result = super().save()
        if self.schedule:
            task_id = 'make_a_post_{}'.format(self.id)
            celery.app.control.revoke(task_id)
            tasks.notify_user.apply_async(
                args=[self.account.telegram_id, '{} at {}'.format(task_id, self.schedule)],
                eta=self.schedule,
                task_id=task_id,
            )

        return result

    @classmethod
    def get(cls, _id, values=False):
        from smm_admin.models import Link

        obj = cls.objects.select_related(
            'account',
        )
        if values:
            obj = obj.values()

        obj = obj.get(id=_id)
        obj.links_list = Link.for_post(post_id=_id)

        return obj

    @property
    def ok(self):
        return all((r.ok for r in self.results.all()))

    def get_url(self):
        return '{}{}'.format(
            settings.DOMAIN_NAME,
            reverse('admin:smm_admin_post_change', args=[self.id]),
        )
