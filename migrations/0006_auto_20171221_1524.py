# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-21 15:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('word_finding', '0005_exercise_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question',
            field=models.TextField(),
        ),
    ]
