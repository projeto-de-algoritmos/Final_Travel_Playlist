# Generated by Django 3.2.8 on 2021-10-20 04:04

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playlist_manager', '0003_graph'),
    ]

    operations = [
        migrations.AddField(
            model_name='graph',
            name='destination',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='graph',
            name='duration',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='graph',
            name='nodes',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=list, size=None),
        ),
        migrations.AddField(
            model_name='graph',
            name='origin',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='graph',
            name='path',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=list, size=None),
        ),
    ]