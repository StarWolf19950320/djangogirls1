# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-06 21:13
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20160815_1701'),
        ('applications', '0020_auto_20161201_1035'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='event',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Event'),
        ),
    ]
