# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-18 10:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('horaris', '0003_auto_20170516_1513'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quatri',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('codigo', models.CharField(max_length=200)),
                ('facultad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='horaris.Facultad')),
            ],
        ),
    ]
