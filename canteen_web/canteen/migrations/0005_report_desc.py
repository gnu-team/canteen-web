# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-19 22:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canteen', '0004_lat_long'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='description',
            field=models.CharField(default='', max_length=256),
        ),
    ]