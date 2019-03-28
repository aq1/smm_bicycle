from django.db import models


class LinkType(models.Model):

    name = models.CharField(max_length=255)
    logo = models.ImageField(blank=True, null=True)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name
