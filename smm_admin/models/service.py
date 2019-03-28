from django.utils.functional import cached_property
from django.contrib.postgres.fields import JSONField
from django.db import models

from smm_admin.services import (
    SERVICES,
    SERVICES_CHOICES,
)


class Service(models.Model):
    account = models.ForeignKey(
        'smm_admin.Account',
        on_delete=models.CASCADE,
        related_name='services',
    )
    type = models.PositiveSmallIntegerField(
        choices=SERVICES_CHOICES,
    )

    data = JSONField()

    def __str__(self):
        return '{} service'.format(self.get_type_display())

    @cached_property
    def service(self):
        return SERVICES[self.type](self)

    def save(self, **kwargs):
        self.service.clean()
        return super().save()
