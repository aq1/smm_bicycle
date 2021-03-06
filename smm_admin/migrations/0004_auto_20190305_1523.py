# Generated by Django 2.1.7 on 2019-03-05 12:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('smm_admin', '0003_auto_20190305_1406'),
    ]

    operations = [
        migrations.RenameField(
            model_name='postresult',
            old_name='post_id',
            new_name='post_id_raw',
        ),
        migrations.AddField(
            model_name='post',
            name='schedule',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='postresult',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='results', to='smm_admin.Post'),
        ),
    ]
