# Generated by Django 2.1.7 on 2019-04-07 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smm_admin', '0024_auto_20190407_2221'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='links',
        ),
        migrations.AddField(
            model_name='post',
            name='artstation',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='post',
            name='instagram',
            field=models.CharField(blank=True, default='', max_length=256),
        ),
    ]
