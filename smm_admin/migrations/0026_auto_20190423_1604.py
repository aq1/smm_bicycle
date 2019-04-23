# Generated by Django 2.1.7 on 2019-04-23 13:04

from django.db import migrations, models
import smm_admin.models.post


class Migration(migrations.Migration):

    dependencies = [
        ('smm_admin', '0025_auto_20190407_2223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='token',
            field=models.CharField(blank=True, default=smm_admin.models.post.generate_token, max_length=32, unique=True),
        ),
    ]
