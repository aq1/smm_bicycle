from django.db import models


class Log(models.Model):

    username = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploaded_log_files', blank=True)
    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
