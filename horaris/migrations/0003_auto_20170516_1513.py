# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-16 15:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horaris', '0002_auto_20170516_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='carrera',
            name='codigo',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='carrera',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]
