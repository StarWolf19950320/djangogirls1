# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-24 13:00
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_auto_20170116_1025'),
    ]

    database_operations = [
        migrations.AlterModelTable('Coach', 'coach_coach')
    ]

    state_operations = [
        migrations.DeleteModel('Coach'),

        migrations.RemoveField(
            model_name='eventpagecontent',
            name='coaches',
        ),

        migrations.AddField(
            model_name='eventpagecontent',
            name='coaches',
            field=models.ManyToManyField(to='coach.Coach', verbose_name='Coaches'),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations
        ),
    ]
