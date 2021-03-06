# Generated by Django 2.1.7 on 2019-03-05 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smm_admin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_id', models.IntegerField()),
                ('service', models.CharField(max_length=255)),
                ('raw', models.TextField()),
                ('text', models.TextField()),
                ('ok', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
