# Generated by Django 2.1.7 on 2019-04-05 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smm_admin', '0021_auto_20190328_1751'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='tags',
        ),
        migrations.AddField(
            model_name='post',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'In Progress'), (1, 'Not Ready'), (2, 'Ready'), (3, 'OK'), (4, 'Failed')], default=1),
        ),
    ]
