# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-25 13:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('funds', '0013_allow_nullable_round_on_submission'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fundtype',
            options={'verbose_name': 'Fund'},
        ),
        migrations.AlterModelOptions(
            name='labtype',
            options={'verbose_name': 'Lab'},
        ),
    ]
