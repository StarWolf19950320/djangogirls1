# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0014_auto_20150814_0439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='state',
            field=models.CharField(max_length=50, verbose_name='State of the application', null=True, default='submitted', choices=[('submitted', 'Application submitted'), ('accepted', 'Application accepted'), ('rejected', 'Application rejected'), ('waitlisted', 'Application on waiting list'), ('declined', 'Applicant declined')]),
        ),
        migrations.AlterField(
            model_name='email',
            name='recipients_group',
            field=models.CharField(max_length=50, verbose_name='Recipients', help_text='Only people assigned to chosen group will receive this email.', choices=[('submitted', 'Application submitted'), ('accepted', 'Application accepted'), ('rejected', 'Application rejected'), ('waitlisted', 'Application on waiting list'), ('declined', 'Applicant declined'), ('waiting', 'RSVP: Waiting for response'), ('yes', 'RSVP: Confirmed attendance'), ('no', 'RSVP: Rejected invitation')]),
        ),
    ]
