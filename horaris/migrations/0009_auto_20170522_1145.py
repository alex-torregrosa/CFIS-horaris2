# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-22 11:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horaris', '0008_asignatura_loaded'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grupo',
            name='numero',
        ),
        migrations.AddField(
            model_name='asignatura',
            name='lastLoadTime',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='grupo',
            name='codigo',
            field=models.CharField(default=0, max_length=30),
            preserve_default=False,
        ),
    ]
