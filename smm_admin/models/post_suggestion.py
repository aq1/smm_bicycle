import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models


def generate_token():
    return str(uuid.uuid4())


class PostSuggestion(models.Model):

    name_en = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255, blank=True, default='')
    text = models.TextField(blank=True, default='')

    old_work_year = models.PositiveSmallIntegerField()
    new_work_year = models.PositiveSmallIntegerField()

    old_work_image = models.ImageField(upload_to='suggested', null=True, blank=True)
    new_work_image = models.ImageField(upload_to='suggested', null=True, blank=True)

    old_work_url = models.CharField(max_length=4096, default='', blank=True)
    new_work_url = models.CharField(max_length=4096, default='', blank=True)

    links = ArrayField(models.CharField(max_length=2048))

    created_at = models.DateTimeField(auto_now_add=True)
    token = models.CharField(
        max_length=36,
        unique=True,
        blank=True,
        default=generate_token,
    )

    def __str__(self):
        return '{} {}'.format(
            self.id,
            self.name_en,
        )
