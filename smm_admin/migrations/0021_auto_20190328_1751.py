# Generated by Django 2.1.7 on 2019-03-28 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smm_admin', '0020_auto_20190328_0039'),
    ]

    operations = [
        migrations.RenameField(
            model_name='postsuggestion',
            old_name='new_work_image',
            new_name='new_work',
        ),
        migrations.RenameField(
            model_name='postsuggestion',
            old_name='old_work_image',
            new_name='old_work',
        ),
        migrations.AddField(
            model_name='post',
            name='new_work_url',
            field=models.CharField(blank=True, default='', max_length=4096),
        ),
        migrations.AddField(
            model_name='post',
            name='old_work_url',
            field=models.CharField(blank=True, default='', max_length=4096),
        ),
    ]