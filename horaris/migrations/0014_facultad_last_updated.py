# Generated by Django 2.0.2 on 2018-06-13 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horaris', '0013_auto_20170806_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='facultad',
            name='last_updated',
            field=models.DateField(auto_now=True),
        ),
    ]