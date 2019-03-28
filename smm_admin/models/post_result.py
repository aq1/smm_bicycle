from django.db import models


class PostResult(models.Model):

    # If post was deleted
    post_id_raw = models.IntegerField()
    post = models.ForeignKey(
        'smm_admin.Post',
        related_name='results',
        on_delete=models.SET_NULL,
        null=True,
    )

    service = models.CharField(max_length=255)

    raw = models.TextField(default='', blank=True)
    text = models.TextField()
    ok = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} {} {}'.format(
            self.post_id_raw,
            self.service,
            self.ok,
        )

    def error(self, text='', raw=''):
        self.ok = False
        self.text = text
        self.raw = raw
        return self

    def success(self, text='', raw=''):
        self.ok = True
        self.text = text
        self.raw = raw
        return self

    def save(self, **kwargs):
        if not isinstance(self.service, str):
            self.service = self.service.name

        return super().save(**kwargs)
