# Generated by Django 3.2.7 on 2022-04-22 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20220422_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='is_frozen',
            field=models.BooleanField(default=False, verbose_name='Event frozen'),
        ),
    ]
