# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-23 14:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horaris', '0009_auto_20170522_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='grupo',
            name='horario',
            field=models.CharField(default='{}', max_length=900),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='grupo',
            name='name',
            field=models.CharField(default=0, max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='grupo',
            name='subgrupo',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
