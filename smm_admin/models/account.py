from django.db import models
from django.contrib.auth import get_user_model

from easy_thumbnails.fields import ThumbnailerImageField


class Account(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        primary_key=True,
        on_delete=models.CASCADE,
    )
    logo = ThumbnailerImageField(
        null=True,
        blank=True,
    )
    telegram_id = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.user)
