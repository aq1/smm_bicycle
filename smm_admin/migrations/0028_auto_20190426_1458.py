# Generated by Django 2.1.7 on 2019-04-26 11:58

from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('smm_admin', '0027_auto_20190424_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='new_work',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='post',
            name='old_work',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='post',
            name='rendered_image',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to=''),
        ),
    ]
